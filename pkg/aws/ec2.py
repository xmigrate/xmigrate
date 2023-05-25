from model.blueprint import Blueprint
from model.disk import Disk
from model.project import Project
import boto3
from sqlalchemy import update


async def create_machine(project, subnet_id, ami_id, machine_type, hostname, db):
    try:
        prjct = db.query(Project).filter(Project.name==project).first()
        public_route = True if (db.query(Blueprint).filter(Blueprint.project==project, Blueprint.image_id==ami_id).first()).public_route else False

        session = boto3.Session(aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=prjct.location)
        ec2 = session.resource('ec2')
        client = boto3.client('ec2',aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=prjct.location)

        filters = [{'Name': 'name','Values': [ami_id]}]
        response = client.describe_images(Filters=filters)

        ami_id = response['Images'][0]['ImageId']
        disks = db.query(Disk).filter(Disk.project==project, Disk.host==hostname).all()
        vol_ids = []
        for disk in disks:
            if disk.mnt_path not in ['slash', 'slashboot']:
                dev_id = ord('f')
                vol_ids.append(
                    {
                    'DeviceName': '/dev/sd'+chr(dev_id),
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'SnapshotId': disk.disk_id,
                        'VolumeType': 'gp3',
                        'Encrypted': False
                    },
                },
                )
                dev_id = dev_id + 1

        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==hostname
            ).values(
            tatus='95'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        instances = ec2.create_instances(
            BlockDeviceMappings=vol_ids,
            ImageId=ami_id, 
            InstanceType=machine_type, 
            MaxCount=1, 
            MinCount=1, 
            NetworkInterfaces=[{'SubnetId': subnet_id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': public_route}]
            )
        
        instances[0].wait_until_running()
        instance_id = instances[0].id
        running_instances = ec2.instances.filter(InstanceIds=[instance_id])
        ip = ''

        for instance in running_instances:
            ip = instance.public_ip_address

            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==hostname
                ).values(
                vm_id=str(instances[0].id), ip=str(ip), status='100'
                ).execution_options(synchronize_session="fetch"))
            db.commit()
    except Exception as e:
        print(repr(e))
        
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==hostname
            ).values(
            status='-100'
            ).execution_options(synchronize_session="fetch"))
        db.commit()


async def build_ec2(project, hostname, db):
    try:
        hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()
        for host in hosts:
            await create_machine(project, host.subnet_id, host.image_id, host.machine_type, hostname, db)
        return True
    except Exception as e:
        print(str(e))
        print(repr(e))
        return False
    

def ec2_instance_types(ec2, region_name):
    describe_args = {}
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']



def get_vm_types(project, db):
    location = ''
    machine_types = []
    try:
        prjct = db.query(Project).filter(Project.name==project).first()
        location = prjct.location
        client = boto3.client('ec2', aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=location)
        for ec2_type in ec2_instance_types(client, location):
            cores = ''
            if 'DefaultCores' in ec2_type['VCpuInfo'].keys():
                cores = ec2_type['VCpuInfo']['DefaultCores']
            else:
                cores = str(ec2_type['VCpuInfo']['DefaultVCpus'])+'_vcpus'
            machine_types.append({"vm_name": ec2_type['InstanceType'], "cores": cores, "memory": ec2_type['MemoryInfo']['SizeInMiB']})
        flag = True
    except Exception as e:
        print(repr(e))
        flag = False
    return machine_types, flag