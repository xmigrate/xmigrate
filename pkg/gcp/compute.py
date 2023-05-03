import time
from mongoengine import *
from model.blueprint import *
from model.disk import *
from utils.dbconn import *
from model.project import *
from .gcp import get_service_compute_v1
from .gcp import REGIONS
from .network import get_vpc
from .network import get_subnet


def list_machine_type(project_id, service_account_json, zone):
    service = get_service_compute_v1(service_account_json)
    request = service.machineTypes().list(project=project_id, zone=zone)
    machine_types = []
    while request is not None:
        response = request.execute()

        for machine_type in response['items']:
            machine_types.append(machine_type['name'])
        request = service.machineTypes().list_next(
            previous_request=request, previous_response=response)
    return machine_types

def get_vm_types(project):
    location = ''
    machine_types = []
    try:
        con = create_db_con()
        service_account = Project.objects(name=project).allow_filtering()[0]['service_account']
        location = Project.objects(name=project).allow_filtering()[0]['location']
        project_id = Project.objects(name=project).allow_filtering()[0]['gcp_project_id']
        machines = list_machine_type(project_id, service_account, location+'-a')
        for machine in machines:
            machine_types.append({'vm_name': machine})
        flag = True
    except Exception as e:
        print(repr(e))
        flag = False
    finally:
        con.shutdown()
    return machine_types, flag


async def create_vm(project_id, service_account_json, vm_name, region, zone_name, os_source, machine_type, network, subnet, additional_disk=[]):
    service = get_service_compute_v1(service_account_json)
    vm_type = "zones/"+zone_name+"/machineTypes/"+machine_type
    network = get_vpc(project_id, service_account_json, network)['selfLink']
    subnet = get_subnet(project_id, service_account_json,
                        subnet, region)['selfLink']
    # image_response = compute.images().getFromFamily(
    #     project='debian-cloud', family='debian-9').execute()
    # source_disk_image = image_response['selfLink']
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
        "name": vm_name.replace('.','-'),
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
    request = service.instances().insert(
        project=project_id, zone=zone_name, body=instance_body)
    response = request.execute()
    while True:
        result = service.zoneOperations().get(project=project_id, zone=zone_name, operation=response['name']).execute()
        print(result)
        if result['status'] == 'DONE':
            return result
        time.sleep(10)


async def build_compute(project, hostname):
    try:
        con = create_db_con()
        hosts = BluePrint.objects(project=project, host=hostname).allow_filtering()
        location = Project.objects(name=project).allow_filtering()[0]['location']
        project_id = Project.objects(name=project).allow_filtering()[0]['gcp_project_id']
        service_account = Project.objects(name=project).allow_filtering()[0]['service_account']

        for host in hosts:
            machine_type = host['machine_type']
            public_route = host['public_route']
            image_id = host['image_id']
            subnet = host['subnet_id'].split('v1')[1].split('/')[-1]
            network = host['vpc_id'].split('v1')[1].split('/')[-1]
            disks = Disk.objects(host=hostname, project=project).allow_filtering()
            extra_disks = []
            for disk in disks:
                if disk["mnt_path"] in ["slash", "slashboot"]:
                    continue
                else:
                    extra_disks.append(
                        {
                            'boot': True if disk["mnt_path"] in ["slash", "slashboot"] else False,
                            'autoDelete': True,
                            "source": disk['disk_id']
                        }
                    )
            print("Extra disks!!")
            print(extra_disks)
            try:
                BluePrint.objects(project=project, host=hostname).update(status='95')
                vm = await create_vm(project_id, service_account, hostname, location, location+"-a", image_id, machine_type, network, subnet, extra_disks)
                if 'error' not in vm.keys():
                    print(f"vm {hostname.replace('.','-')} created.")
                    BluePrint.objects(project=project, host=hostname).update(status='100')
                else:
                    print(f"vm {hostname.replace('.','-')} creation failed.")
                    BluePrint.objects(project=project, host=hostname).update(status='-100')
                ## todo watch vm status 
                con.shutdown()
                return True
            except Exception as e:
                print(e)
                con.shutdown()
                return False
        return True
    except Exception as e:
        print(str(e))
        print(repr(e))
        return False
    finally:
        con.shutdown()
