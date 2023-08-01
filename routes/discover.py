from pkg.aws.aws_config import write_aws_creds
from pkg.common.nodes import add_nodes
from routes.auth import TokenData, get_current_user
from schemas.discover import DiscoverBase, DiscoverCreate, DiscoverUpdate
from schemas.disk import DiskCreate, DiskUpdate
from schemas.machines import VMCreate, VMUpdate
from schemas.node import NodeCreate, NodeUpdate
from services.blueprint import check_blueprint_exists, create_blueprint, get_blueprintid
from services.discover import check_discover_exists, create_discover, get_discoverid, update_discover
from services.disk import check_disk_exists, create_disk, get_diskid,update_disk
from services.machines import check_vm_exists, create_vm, get_machineid, update_vm
from services.node import check_node_exists, create_node, get_nodeid, update_node
from services.project import get_projectid
from pkg.test_header_files.test_data import discover_test_data
from utils.constants import Provider, Test
from utils.database import dbconn
from utils.playbook import run_playbook
import netaddr, re, os
from fastapi import APIRouter, Depends, HTTPException, Request, status 
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.post('/discover')
async def discover(data: DiscoverBase, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = request.headers.get(Test.HEADER.value)
    current_dir = os.getcwd()
    project = data.project
    project_id = get_projectid(current_user['username'], project, db)

    if add_nodes(data.hosts, data.username, data.password, project) == False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"message": "request couldn't process"}))
    else:
        node_exists = check_node_exists(project_id, db)
        if not node_exists:
            node_data = NodeCreate(project_id=project_id, hosts=data.hosts, username=data.username, password=data.password)
            create_node(node_data, db)
        else:
            node_id = get_nodeid(project_id, db)
            node_data = NodeUpdate(node_id=node_id, hosts=data.hosts, username=data.username, password=data.password)
            update_node(node_data, db)
    
    if data.provider == Provider.AWS.value:
        write_aws_creds(current_user['username'], project, db)
    
    if test_header is not None:
        try:
            await discover_test_data(project, project_id, db)
            return jsonable_encoder({'status': '200'})
        except Exception as e:
            print("Some error with adding test_data!")
            return jsonable_encoder({'status': '400'})
    
    PLAYBOOK = "gather_facts.yaml"
    STAGE = "gather_facts"    
    
    try:
        finished, output = run_playbook(provider="common", username=data.username, project_name=project, curr_working_dir=current_dir, playbook=PLAYBOOK, stage=STAGE)
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
                    diskinfo = disk.strip().split()
                    del diskinfo[-1] # the final element in the list is only needed during filtering in ansible
                    hashmap = dict(zip(keys, diskinfo))
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
                    discover_exists = check_discover_exists(project_id, db)
                    if not discover_exists:
                        discover_data = DiscoverCreate(project_id=project_id, hostname=hostname, network=network, subnet=subnet, cpu_core=cores, cpu_model=cpu_model, ram=ram, disk_details=disks, ip=ip_address)
                        create_discover(discover_data, db)
                    else:
                        discover_id = get_discoverid(project_id, db)
                        discover_data = DiscoverUpdate(discover_id=discover_id, hostname=hostname, network=network, subnet=subnet, cpu_core=cores, cpu_model=cpu_model, ram=ram, disk_details=disks, ip=ip_address)
                        update_discover(discover_data, db)

                    blueprint_exists = check_blueprint_exists(project_id, db)
                    if not blueprint_exists:
                        create_blueprint(project_id, db)

                    blueprint_id = get_blueprintid(project_id, db)
                    vm_exists = check_vm_exists(hostname, blueprint_id, db)
                    if not vm_exists:
                        vm_data = VMCreate(blueprint_id=blueprint_id, hostname=hostname, network=network, cpu_core=cores, cpu_model=cpu_model, ram=ram)
                        create_vm(vm_data, db)
                    else:
                        machine_id = get_machineid(hostname, blueprint_id, db)
                        vm_data = VMUpdate(machine_id=machine_id, network=network, cpu_core=cores, cpu_model=cpu_model, ram=ram)
                        update_vm(vm_data, db)

                    machine_id = get_machineid(hostname, blueprint_id, db)
                    for disk in disks:
                        mnt_path = disk['mnt_path'].replace('/', 'slash')
                        disk_exists = check_disk_exists(machine_id, mnt_path, db)
                        if not disk_exists:
                            disk_data = DiskCreate(hostname=hostname, mnt_path=mnt_path, vm_id=machine_id)
                            create_disk(disk_data, db)
                        else:
                            disk_id = get_diskid(machine_id, mnt_path, db)
                            disk_data = DiskUpdate(disk_id=disk_id, hostname=hostname, mnt_path=mnt_path, vm_id=machine_id)
                            update_disk(disk_data, db)
                except Exception as e:
                    print("Error: "+ str(e))
            return jsonable_encoder({'status': '200'})
        else:
            print("VM data discovery failed!")
            return jsonable_encoder({'status': '400'})
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"message": "request couldn't process"}))
