from app import app
from utils.dbconn import *
from model.discover import Discover as DiscoverM
from model.project import *
from model.storage import *
from pkg.common import nodes as n
import os, netaddr
from quart import jsonify, request
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi import Depends
from routes.auth import TokenData, get_current_user
from typing import Union
from dotenv import load_dotenv
from os import getenv
from utils.playbook import run_playbook

class Discover(BaseModel):
    provider: Union[str,None] = None
    hosts: Union[list,None] = None
    username: Union[str,None] = None
    password: Union[str,None] = None
    project: Union[str,None] = None

@app.post('/discover')
async def discover(data: Discover, current_user: TokenData = Depends(get_current_user)):
    con = create_db_con()
    current_dir = os.getcwd()
    print(data)
    provider = data.provider
    nodes = data.hosts
    username = data.username
    password = data.password
    project = data.project
    load_dotenv()
    mongodb = os.getenv('BASE_URL')
    if n.add_nodes(nodes,username,password, project) == False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder(
            {"msg": "Request couldn't process"}))

    playbook = "gather_facts.yaml"
    stage = "gather_facts"
        
    if provider == "aws":
        proj_details = Project.objects(name=project)[0]
        access_key = proj_details['access_key']
        secret_key = proj_details['secret_key']
        location = proj_details['location']
        credentials_str = '['+project+']\naws_access_key_id = '+ access_key+'\n'+ 'aws_secret_access_key = '+secret_key
        aws_dir = os.path.expanduser('~/.aws')
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)
        with open(aws_dir+'/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+project+']\nregion = '+location+'\noutput = json'
        with open(aws_dir+'/config', 'w+') as writer:
            writer.write(config_str)
    try:
        output = run_playbook(provider=provider, username=username, project_name=project, curr_working_dir=current_dir, playbook=playbook, stage=stage)
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
            cpu_model = facts['ansible_processor'][2]
            ram = str(facts['ansible_memtotal_mb'])
            disks = []
            keys = ['filesystem', 'disk_size', 'uuid', 'dev', 'mnt_path']
            for disk in disk_details:
                hashmap = {}
                diskinfo = disk.strip().split()
                _ = list(map(lambda k, v: hashmap.update({k:v}), keys, diskinfo))
                disks.append(hashmap)
            try:
                DiscoverM.objects(project=project,host=hostname).update(ip=ip_address, subnet=subnet, network=network,
                        ports=ports, cores=cores, cpu_model=cpu_model, ram=ram, disk_details=disks)
            except Exception as e:
                print("Error: "+str(e))
            finally:
                con.shutdown()
        return jsonable_encoder({'status': '200'})
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder(
            {"msg": "Request couldn't process"}))
