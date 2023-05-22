from model.blueprint import Blueprint
from model.discover import Discover as DiscoverM
from model.project import Project as ProjectM
from utils.database import dbconn
from utils.playbook import run_playbook
from pkg.common import nodes as n
import os, netaddr
from typing import Union
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.orm import Session

router = APIRouter()

class Discover(BaseModel):
    provider: Union[str,None] = None
    hosts: Union[list,None] = None
    username: Union[str,None] = None
    password: Union[str,None] = None
    project: Union[str,None] = None

@router.post('/discover')
async def discover(data: Discover, db: Session = Depends(dbconn)):
    current_dir = os.getcwd()

    provider = data.provider
    nodes = data.hosts
    username = data.username
    password = data.password
    project = data.project

    if n.add_nodes(nodes, username, password, project, db) == False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=jsonable_encoder({"msg": "Request couldn't process"}))

    playbook = "gather_facts.yaml"
    stage = "gather_facts"
        
    if provider == "aws":
        proj_details = db.query(ProjectM).filter(ProjectM.name==project).first()
    
        aws_dir = os.path.expanduser('~/.aws')
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)

        with open(f'{aws_dir}/credentials', 'w+') as cred, open(f'{aws_dir}/config', 'w+') as config:
            cred.write(f'[{project}]\naws_access_key_id = {proj_details.access_key}\naws_secret_access_key = {proj_details.secret_key}')
            config.write(f'[profile {project}]\nregion = {proj_details.location}\noutput = json')
    try:
        finished, output = run_playbook(provider=provider, username=username, project_name=project, curr_working_dir=current_dir, playbook=playbook, stage=stage)
        if finished:
            if 'ok' in output.stats.keys():
                linux_host = list(output.stats['ok'].keys())[0]
                facts = output.get_fact_cache(host=linux_host)
                disk_details = []
                for e in output.events:
                    if "event_data" in e.keys():
                        if "res" in e['event_data'].keys():
                            if "disk_info.stdout_lines" in e['event_data']['res'].keys():
                                disk_details = e['event_data']['res']['disk_info.stdout_lines']
                hostname = facts['ansible_hostname']
                ip_address = facts['ansible_all_ipv4_addresses'][0]
                nwinfo = netaddr.IPNetwork(f'{facts["ansible_default_ipv4"]["address"]}/{facts["ansible_default_ipv4"]["netmask"]}')
                subnet = str(nwinfo)
                network = str(nwinfo.network)
                ports = []
                cores = str(facts['ansible_processor_cores'])
                cpu_model = facts['ansible_processor'][2] if len(facts['ansible_processor']) > 2 and len(facts['ansible_processor'][2]) > 1 else ' '
                ram = str(facts['ansible_memtotal_mb'])
                disks = []
                keys = ['filesystem', 'disk_size', 'uuid', 'dev', 'mnt_path']
                for disk in disk_details:
                    hashmap = {}
                    diskinfo = disk.strip().split()
                    _ = list(map(lambda k, v: hashmap.update({k:v}), keys, diskinfo))
                    hashmap['dev'] = f'/dev/{hashmap["dev"]}'
                    disks.append(hashmap)
                try:
                    if db.query(DiscoverM).filter(DiscoverM.project==project,DiscoverM.host==hostname).count() == 0:
                        dscvr = DiscoverM(project=project, host=hostname, ip=ip_address, subnet=subnet, network=network, ports=ports, cores=cores, cpu_model=cpu_model, ram=ram, disk_details=disks, public_ip=','.join(nodes))
                        db.add(dscvr)
                        db.commit()
                        db.refresh(dscvr)
                    else:
                        db.execute(update(DiscoverM).where(
                            DiscoverM.project==project and DiscoverM.host==hostname
                            ).values(
                            ip=ip_address, subnet=subnet, network=network, ports=ports, cores=cores, cpu_model=cpu_model, ram=ram, disk_details=disks
                            ).execution_options(synchronize_session="fetch"))
                        db.commit()

                    if db.query(Blueprint).filter(Blueprint.project==project,Blueprint.host==hostname).count() == 0:
                        blrpnt = Blueprint(project=project, host=hostname, ip=ip_address, subnet=subnet, network=network, cpu_model=cpu_model, ram=ram, machine_type=' ')
                        db.add(blrpnt)
                        db.commit()
                        db.refresh(blrpnt)
                except Exception as e:
                    print("Error: "+str(e))
            return jsonable_encoder({'status': '200'})
        else:
            print("VM preparation failed!")
            return jsonable_encoder({'status': '400'})
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder(
            {"msg": "Request couldn't process"}))
