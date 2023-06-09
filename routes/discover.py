from pkg.aws.aws_config import write_aws_creds
from routes.auth import TokenData, get_current_user
from services.blueprint import check_blueprint_exists, create_blueprint, get_blueprintid
from services.discover import check_discover_exists, create_discover, get_discoverid, update_discover
from services.disk import check_disk_exists, create_disk
from services.project import get_projectid, get_project_by_name
from schemas.discover import DiscoverBase
from utils.database import dbconn
from utils.playbook import run_playbook
from pkg.common import nodes as n
import os, netaddr, re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.post('/discover')
async def discover(data: DiscoverBase, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    current_dir = os.getcwd()
    project = data.project

    if n.add_nodes(data.hosts, data.username, data.password, project, db) == False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))

    playbook = "gather_facts.yaml"
    stage = "gather_facts"
        
    if data.provider == "aws":
        proj_details = get_project_by_name(current_user['username'], project, db)
        write_aws_creds(project, proj_details.aws_access_key, proj_details.aws_secret_key, proj_details.location)
    try:
        finished, output = run_playbook(provider=data.provider, username=data.username, project_name=project, curr_working_dir=current_dir, playbook=playbook, stage=stage)
        if finished:
            if 'ok' in output.stats.keys():
                linux_host = list(output.stats['ok'].keys())[0]
                facts = output.get_fact_cache(host=linux_host)
                disk_details = []
                blkid = []
                for e in output.events:
                    if "event_data" in e.keys():
                        if "res" in e['event_data'].keys():
                            if "disk_info.stdout_lines" in e['event_data']['res'].keys():
                                disk_details = e['event_data']['res']['disk_info.stdout_lines']
                            if "blkid.stdout_lines" in e['event_data']['res'].keys():
                                blkid = e['event_data']['res']['blkid.stdout_lines']
                hostname = str(facts['ansible_hostname'])
                ip_address = facts['ansible_all_ipv4_addresses'][0]
                nwinfo = netaddr.IPNetwork(f'{facts["ansible_default_ipv4"]["address"]}/{facts["ansible_default_ipv4"]["netmask"]}')
                subnet = str(nwinfo)
                network = str(nwinfo.network)
                cores = int(facts['ansible_processor_cores'])
                cpu_model = facts['ansible_processor'][2] if len(facts['ansible_processor']) > 2 and len(facts['ansible_processor'][2]) > 1 else ' '
                ram = str(facts['ansible_memtotal_mb'])
                disks = []
                dev_list=  []
                keys = ['filesystem', 'disk_size', 'uuid', 'dev', 'mnt_path']
                for disk in disk_details:
                    hashmap = {}
                    diskinfo = disk.strip().split()
                    diskinfo.pop(-1) # the final element in the list is only needed during filtering in ansible
                    _ = list(map(lambda k, v: hashmap.update({k:v}), keys, diskinfo))
                    hashmap['dev'] = hashmap['dev'][:-2] if 'nvme' in hashmap['dev'] else (hashmap['dev']).rstrip('1234567890')
                    if hashmap['dev'] not in dev_list:
                        for blk in blkid:
                            if hashmap['dev'] in blk and 'uuid' in blk.lower():
                                matches = re.findall(r'(?i)(\w+UUID)="([^"]+)"', blk)
                                for match in matches:
                                    _, hashmap['uuid'] = match
                                break
                        else:
                            hashmap['uuid'] = ' '
                        dev_list.append(hashmap['dev'])
                        hashmap['dev'] = f'/dev/{hashmap["dev"]}'
                        disks.append(hashmap)
                try:
                    project_id = get_projectid(current_user['username'], project, db)
                    discover_data = project_id, hostname, network, subnet, None, cores, cpu_model, ram, disks, ip_address
                    discover_exists = check_discover_exists(project_id, db)
                    if not discover_exists:
                        create_discover(discover_data, db)
                    else:
                        discover_id = get_discoverid(project_id, db)
                        update_discover(discover_id, discover_data, db)

                    blueprint_exists = check_blueprint_exists(project_id, db)
                    if not blueprint_exists:
                        create_blueprint(project_id, db)

                    blueprint_id = get_blueprintid(project_id, db)
                    for disk in disks:
                        mnt_path = disk['mnt_path'].replace('/', 'slash')
                        disk_exists = check_disk_exists(blueprint_id, mnt_path, db)
                        if not disk_exists:
                            disk_data = hostname, None, '0', mnt_path, None, blueprint_id
                            create_disk(disk_data, db)
                except Exception as e:
                    print("Error: "+str(e))
            return jsonable_encoder({'status': '200'})
        else:
            print("VM preparation failed!")
            return jsonable_encoder({'status': '400'})
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "Request couldn't process"}))
