from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.discover import get_discover
from services.disk import get_diskid, update_disk
from services.machines import get_all_machines, get_machine_by_hostname, update_vm
from services.project import get_project_by_name
from services.storage import get_storage
from utils.logger import *
import asyncio
import json
import boto3


async def start_ami_creation_worker(project, disk_containers, disk_mountpoint, host, db):
   import_task_id = ''
   role_id = "vmimport"

   try:
      client = boto3.client('iam', aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key)
      role_list = [role['RoleName'] for role in client.list_roles()['Roles']]

      if role_id not in role_list:
         file_trust_policy={
            "Version": "2012-10-17",
            "Statement": [
               {
                  "Effect": "Allow",
                  "Principal": { "Service": "vmie.amazonaws.com" },
                  "Action": "sts:AssumeRole",
                  "Condition": {
                     "StringEquals":{
                        "sts:Externalid": 'vmimport'
                     }
                  }
               }
            ]
         }
         
         response = client.create_role(RoleName=role_id, AssumeRolePolicyDocument=json.dumps(file_trust_policy), Description='VM Import/Export role', MaxSessionDuration=7200, Tags=[{'Key': 'app', 'Value': 'xmigrate'}])
         print(f'Created role {role_id}')

         file_role_policy = {
               "Version":"2012-10-17",
               "Statement":[
                  {
                     "Effect": "Allow",
                     "Action": [
                        "kms:CreateGrant",
                        "kms:Decrypt",
                        "kms:DescribeKey",
                        "kms:Encrypt",
                        "kms:GenerateDataKey*",
                        "kms:ReEncrypt*"
                     ],
                     "Resource": "*"
                  },
                  {
                     "Effect": "Allow",
                     "Action": [
                        "license-manager:GetLicenseConfiguration",
                        "license-manager:UpdateLicenseSpecificationsForResource",
                        "license-manager:ListLicenseSpecificationsForResource"
                     ],
                     "Resource": "*"
                  }
               ]
            }
         response = client.put_role_policy(
            RoleName= role_id,
            PolicyName= 'vmimport',
            PolicyDocument= json.dumps(file_role_policy)
         )
         print(f'Attached inline policy vmimport to role {role_id}')
         
         policy_names = ['AmazonEC2FullAccess', 'AmazonS3FullAccess']

         for policy_name in policy_names:
            policy_arn = f'arn:aws:iam::aws:policy/{policy_name}'
            response = client.attach_role_policy(
               RoleName=role_id,
               PolicyArn=policy_arn
            )
            print(f'Attached managed policy {policy_name} to role {role_id}')

         print("Waiting for the role to become available...")
         asyncio.sleep(15)
      else:
         print(f'Role {role_id} already exists, skipping role creation.')
   except Exception as e:
      print(str(e))

      vm_data = VMUpdate(machine_id=host.id, status=-1)
      update_vm(vm_data, db)
   try:
      print("Importing image...")
      client = boto3.client('ec2', aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key, region_name=project.location)

      response = client.import_image(
         DiskContainers=disk_containers,
         RoleName=role_id,
         TagSpecifications=[
            {
               'ResourceType': 'import-image-task',
               'Tags': [
                  {
                     'Key': 'Name',
                     'Value': host.hostname
                  },
               ]
            },
         ]
      )
      import_task_id = response['ImportTaskId']

      vm_data = VMUpdate(machine_id=host.id, status=30)
      update_vm(vm_data, db)

      logger("AMI creation started: "+ import_task_id, "info")

      if len(import_task_id) > 0:
         while True:
            response = client.describe_import_image_tasks(ImportTaskIds=[import_task_id,])
            print(response)
            
            if response['ImportImageTasks'][0]['Status'] == "completed":
               ami_id = import_task_id

               vm_data = VMUpdate(machine_id=host.id, image_id=ami_id, status='35')
               update_vm(vm_data, db)

               for import_task in response['ImportImageTasks']:
                  for snapshot_detail in import_task['SnapshotDetails']:
                        disk_id = get_diskid(host.id, disk_mountpoint.replace('/', 'slash'), db)
                        disk_data = DiskUpdate(disk_id=disk_id, file_size=str(snapshot_detail['DiskImageSize']), target_disk_id=snapshot_detail['SnapshotId'], vhd=snapshot_detail['UserBucket']['S3Key'])
                        update_disk(disk_data, db)
               break
            elif response['ImportImageTasks'][0]['Status'] == "deleted":
               vm_data = VMUpdate(machine_id=host.id, status=-35)
               update_vm(vm_data, db)

               logger(response['ImportImageTasks'][0]['StatusMessage'], 'error')
               print(response['ImportImageTasks'][0]['StatusMessage'])
               return False
            else:
               await asyncio.sleep(60)
   except Exception as e:
      print(str(e))
      logger("Error while creating AMI: "+ str(e), "error")
      
      vm_data = VMUpdate(machine_id=host.id, status=-35)
      update_vm(vm_data, db)

      return False


async def start_ami_creation(user, project, hostname, db) -> bool:
   hosts = []
   try:
      project = get_project_by_name(user, project, db)
      storage = get_storage(project.id, db)
      bucket_name = storage.bucket_name if storage is not None else ''
      blueprint_id = get_blueprintid(project.id, db)

      if hostname == "all":
         hosts = get_all_machines(blueprint_id, db)
      else:
         hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]
   except Exception as e:
      print(repr(e))

   for host in hosts:
      disks = json.loads(get_discover(project.id, db)[0].disk_details)
      disk_containers = []

      for disk in disks:
         image_name = f'{host.hostname}{disk["mnt_path"].replace("/", "-slash")}.img'
         disk_containers.append(
            {
               'Description': 'Xmigrate',
               'Format': 'RAW',
               'UserBucket': {
                     'S3Bucket': bucket_name,
                     'S3Key': image_name
               }
            }
         )
      worker_done = await start_ami_creation_worker(project, disk_containers, disk["mnt_path"], host, db)
      if worker_done == False:
         return False
   return True