from .gcp import get_service_compute_v1
from .network import get_vpc
from .network import get_subnet
from model.blueprint import Blueprint
from model.disk import Disk
from model.project import Project
import asyncio
from sqlalchemy import update


async def create_vm(project_id, service_account_json, vm_name, region, zone_name, os_source, machine_type, network, subnet, additional_disk=[]):
    service = get_service_compute_v1(service_account_json)
    vm_type = f"zones/{zone_name}+machineTypes/{machine_type}"
    network = get_vpc(project_id, service_account_json, network)['selfLink']
    subnet = get_subnet(project_id, service_account_json,
                        subnet, region)['selfLink']
    
    disks = [
        {
            'boot': True,
            'autoDelete': True,
            "initializeParams": {
                "sourceImage": os_source
            }
        }
    ]

    disks.extend(additional_disk)

    instance_body = {
        "name": vm_name.replace('.', '-'),
        "machineType": vm_type,
        "disks": disks,
        'networkInterfaces': [{
            'network': network,
            'subnetwork': subnet,
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }]

    }
    request = service.instances().insert(project=project_id, zone=zone_name, body=instance_body)
    response = request.execute()

    while True:
        result = service.zoneOperations().get(project=project_id, zone=zone_name, operation=response['name']).execute()
        print(result)

        if result['status'] == 'DONE':
            return result
        
        asyncio.sleep(10)


async def build_compute(project, hostname, db):
    try:
        prjct = db.query(Project).filter(Project.name==project).first()
        hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()

        for host in hosts:
            subnet = (host.subnet_id).split('v1')[1].split('/')[-1]
            network = (host.vpc_id).split('v1')[1].split('/')[-1]
            disks = db.query(Disk).filter(Disk.project==project, Disk.host==hostname).all()
            extra_disks = []
            for disk in disks:
                if disk.mnt_path in ["slash", "slashboot"]:
                    continue
                else:
                    extra_disks.append(
                        {
                            'boot': True if disk.mnt_path in ["slash", "slashboot"] else False,
                            'autoDelete': True,
                            "source": disk.disk_id
                        }
                    )
            print("Extra disks!!")
            print(extra_disks)
            try:
                db.execute(update(Blueprint).where(
                    Blueprint.project==project and Blueprint.host==hostname
                    ).values(
                    status='95'
                    ).execution_options(synchronize_session="fetch"))
                db.commit()

                vm = await create_vm(prjct.gcp_project_id, prjct.service_account, hostname, prjct.location, f"{prjct.location}-a", host.image_id, host.machine_type, network, subnet, extra_disks)
                if 'error' not in vm.keys():
                    print(f"vm {hostname.replace('.', '-')} created.")
                    
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==hostname
                        ).values(
                        status='100'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
                else:
                    print(f"vm {hostname.replace('.','-')} creation failed.")
                    
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==hostname
                        ).values(
                        status='-100'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    return False
                ## todo watch vm status 
                return True
            except Exception as e:
                print(e)

                db.execute(update(Blueprint).where(
                    Blueprint.project==project and Blueprint.host==hostname
                    ).values(
                    status='-100'
                    ).execution_options(synchronize_session="fetch"))
                db.commit()

                return False
        return True
    except Exception as e:
        print(str(e))
        print(repr(e))
        return False
