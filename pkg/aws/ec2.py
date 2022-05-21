from mongoengine import *
from model.blueprint import *
from model.disk import *
import boto3
from utils.dbconn import *
import asyncio
from model.project import *
from pkg.aws import creds

async def create_machine(project,subnet_id,ami_id,machine_type,hostname):
    con = create_db_con()
    access_key = Project.objects(name=project).allow_filtering()[0]['access_key']
    secret_key = Project.objects(name=project).allow_filtering()[0]['secret_key']
    location = Project.objects(name=project).allow_filtering()[0]['location']
    public_route = True if BluePrint.objects(project=project, image_id=ami_id).allow_filtering()[0]['public_route'] == "true" else False
    con.shutdown()
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
    ec2 = session.resource('ec2')
    client = boto3.client('ec2',aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
    amiid = ami_id
    filters = [{'Name':'name','Values':[ami_id]}]
    response = client.describe_images(Filters=filters)
    ami_id = response['Images'][0]['ImageId']
    disks = Disk.objects(project=project,host=hostname).allow_filtering()
    vol_ids = []
    for disk in disks:
        if disk['mnt_path'] not in ['slash', 'slashboot']:
            dev_id = ord('f')
            vol_ids.append(
                {
                'DeviceName': '/dev/sd'+chr(dev_id),
                'Ebs': {
                    'DeleteOnTermination': True,
                    'SnapshotId': disk['disk_id'],
                    'VolumeType': 'gp3',
                    'Encrypted': False
                },
              },
            )
            dev_id = dev_id + 1
    BluePrint.objects(project=project,host=hostname).update(status='95')
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
    try:
        BluePrint.objects(project=project,host=hostname).update(vm_id=str(instances[0].id), ip=str(ip))
        BluePrint.objects(project=project,host=hostname).update(status='100')
    except Exception as e:
        print(repr(e))
        BluePrint.objects(project=project,host=hostname).update(status='-100')
    finally:
        con.shutdown()


async def build_ec2(project, hostname):
    try:
        con = create_db_con()
        hosts = BluePrint.objects(project=project, host=hostname).allow_filtering()
        for host in hosts:
            await create_machine(project,host['subnet_id'],host['image_id'],host['machine_type'], hostname)
        con.shutdown()
        return True
    except Exception as e:
        print(str(e))
        print(repr(e))
        return False
    finally:
        con.shutdown()


def ec2_instance_types(ec2,region_name):
    describe_args = {}
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']



def get_vm_types(project):
    location = ''
    machine_types = []
    try:
        con = create_db_con()
        access_key = Project.objects(name=project).allow_filtering()[0]['access_key']
        secret_key = Project.objects(name=project).allow_filtering()[0]['secret_key']
        location = Project.objects(name=project).allow_filtering()[0]['location']
        client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name=location)
        for ec2_type in ec2_instance_types(client,location):
            cores = ''
            if 'DefaultCores' in ec2_type['VCpuInfo'].keys():
                cores = ec2_type['VCpuInfo']['DefaultCores']
            else:
                cores = str(ec2_type['VCpuInfo']['DefaultVCpus'])+'_vcpus'
            machine_types.append({"vm_name":ec2_type['InstanceType'],"cores":cores,"memory":ec2_type['MemoryInfo']['SizeInMiB']})
        flag = True
    except Exception as e:
        print(repr(e))
        flag = False
    finally:
        con.shutdown()
    return machine_types, flag