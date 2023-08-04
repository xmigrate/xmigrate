from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.disk import get_all_disks
from services.machines import get_all_machines, get_machine_by_hostname, update_vm
from services.network import get_all_subnets, get_network_by_cidr
from services.project import get_project_by_name
import boto3


async def create_machine(project, subnet_id, host, db) -> bool:
    try:
        public_route = host.public_route

        session = boto3.Session(aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key, region_name=project.location)
        ec2 = session.resource('ec2')
        client = boto3.client('ec2', aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key, region_name=project.location)

        filters = [{'Name': 'name', 'Values': [host.image_id]}]
        response = client.describe_images(Filters=filters)

        ami_id = response['Images'][0]['ImageId']
        disks = get_all_disks(host.id, db)
        vol_ids = []
        
        for disk in disks:
            if disk.mnt_path not in ['slash', 'slashboot']:
                dev_id = ord('f')
                vol_ids.append(
                    {
                    'DeviceName': '/dev/sd' + chr(dev_id),
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'SnapshotId': disk.target_disk_id,
                        'VolumeType': 'gp3',
                        'Encrypted': False
                        },
                    },
                )
                dev_id += 1

        vm_data = VMUpdate(machine_id=host.id, status=95)
        update_vm(vm_data, db)

        instances = ec2.create_instances(
            BlockDeviceMappings=vol_ids,
            ImageId=ami_id, 
            InstanceType=host.machine_type, 
            MaxCount=1, 
            MinCount=1, 
            NetworkInterfaces=[{'SubnetId': subnet_id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': public_route}]
            )
        
        instances[0].wait_until_running()
        instance_id = instances[0].id
        running_instances = ec2.instances.filter(InstanceIds=[instance_id])
        ip = ''

        for instance in running_instances:
            if instance.id == instance_id:
                ip = instance.public_ip_address
                vm_data = VMUpdate(machine_id=host.id, vm_id=str(instances[0].id), ip=str(ip), status=100)
                update_vm(vm_data, db)
                break
        return True
    except Exception as e:
        print(repr(e))
        vm_data = VMUpdate(machine_id=host.id, status=-100)
        update_vm(vm_data, db)
        return False


async def build_ec2(user, project, hostname, db) -> bool:
    try:
        project = get_project_by_name(user, project, db)
        blueprint_id = get_blueprintid(project.id, db)

        if hostname == ["all"]:
            hosts = get_all_machines(blueprint_id, db)
        else:
            hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]

        for host in hosts:
            network = get_network_by_cidr(host.network, blueprint_id, db)
            subnet = get_all_subnets(network.id, db)[0]
            machine_created = await create_machine(project, subnet.target_subnet_id, host, db)
            if not machine_created: return False
        return True
    except Exception as e:
        print(str(e))
        return False