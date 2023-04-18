import time, json
from mongoengine import *
from model.discover import *
from model.blueprint import *
from model.disk import *
from utils.dbconn import *
from model.storage import Bucket
from model.project import *
import asyncio
from pkg.aws import creds
import boto3
from utils.logger import *

async def start_ami_creation_worker(bucket_name, image_name, project, disk_containers, hostname):
   con = create_db_con()
   access_key = Project.objects(name=project).allow_filtering()[0]['access_key']
   secret_key = Project.objects(name=project).allow_filtering()[0]['secret_key']
   region = Project.objects(name=project).allow_filtering()[0]['location']
   import_task_id = ''
   role_id = "vmimport"
   try:
      client = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

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
         
         response = client.create_role(RoleName=role_id, AssumeRolePolicyDocument=json.dumps(file_trust_policy), Description='For vm migration', MaxSessionDuration=7200, Tags=[{'Key': 'app','Value': 'xmigrate'}])
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
         time.sleep(15)
      else:
         print(f'Role {role_id} already exists, skipping role creation')
   except Exception as e:
      print(str(e))
      BluePrint.objects(project=project, host=hostname).update(status='-1')
   try:
      print("Importing image")
      client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
      response = client.import_image(
         DiskContainers=disk_containers,
         RoleName=role_id,
         TagSpecifications=[
            {
               'ResourceType': 'import-image-task',
               'Tags': [
                  {
                     'Key': 'Name',
                     'Value': hostname
                  },
               ]
            },
         ]
      )
      import_task_id = response['ImportTaskId']
      BluePrint.objects(host=hostname, project=project).update(status='30')
      logger("AMI creation started: "+import_task_id,"info")
      if len(import_task_id) > 0:
         while True:
            response = client.describe_import_image_tasks(
               ImportTaskIds=[
               import_task_id,
               ]
            )
            if response['ImportImageTasks'][0]['Status'] == "completed":
               ami_id = import_task_id
               BluePrint.objects(host=hostname, project=project).update(image_id=ami_id, status='35')
               for import_task in response['ImportImageTasks']:
                  for snapshot_detail in import_task['SnapshotDetails']:
                     Disk.objects(host=hostname, project=project, mnt_path=snapshot_detail['UserBucket']['S3Key'].split('-')[1].split('.')[0]).update(
                        file_size=str(snapshot_detail['DiskImageSize']), disk_id=snapshot_detail['SnapshotId'], 
                        vhd=snapshot_detail['UserBucket']['S3Key'])
               break
            elif response['ImportImageTasks'][0]['Status'] == "deleted":
               BluePrint.objects(host=hostname, project=project).update(status='-35')
               logger(response['ImportImageTasks'][0]['StatusMessage'],'error')
               print(response['ImportImageTasks'][0]['StatusMessage'])
               break
            else:
               print(response)
               await asyncio.sleep(60)
   except Exception as e:
      print(str(e))
      logger("Error while creating AMI:"+str(e),"error")
      BluePrint.objects(host=hostname, project=project).update(status='-35')
      return False
   finally:
      con.shutdown()


async def start_ami_creation(project, hostname):
   set_creds = creds.set_aws_creds(project)
   con = create_db_con()
   bucket_name = ''
   hosts = []
   try:
      bucket = Bucket.objects(project=project).allow_filtering()[0]
      if hostname == "all":
         hosts = BluePrint.objects(project=project).allow_filtering()
      else:
         hosts = BluePrint.objects(project=project,host=hostname).allow_filtering()
      bucket_name = bucket['bucket']
   except Exception as e:
      print(repr(e))
   finally:
      con.shutdown()
   for host in hosts:
      disks = Discover.objects(project=project,host=host['host']).allow_filtering()[0]['disk_details']
      disk_containers = [] 
      for disk in disks:
         image_name = host['host']+disk['mnt_path'].replace("/","-slash")+'.img'
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
      worker_done = await start_ami_creation_worker(bucket_name, image_name, project, disk_containers, hostname)
      if worker_done == False:
         return False
   return True