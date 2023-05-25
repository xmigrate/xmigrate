from model.blueprint import Blueprint
from model.discover import Discover
from model.disk import Disk
from model.project import Project
from model.storage import Bucket
from pkg.aws import creds
from utils.logger import *
import asyncio
import json
import boto3
from sqlalchemy import update

async def start_ami_creation_worker(project, disk_containers, hostname, db):
   prjct = db.query(Project).filter(Project.name==project).first()
   import_task_id = ''
   role_id = "vmimport"

   try:
      client = boto3.client('iam', aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key)
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
         asyncio.sleep(15)
      else:
         print(f'Role {role_id} already exists, skipping role creation.')
   except Exception as e:
      print(str(e))

      db.execute(update(Blueprint).where(
         Blueprint.project==project and Blueprint.host==hostname
         ).values(
         status='-1'
         ).execution_options(synchronize_session="fetch"))
      db.commit()
   try:
      print("Importing image...")
      client = boto3.client('ec2', aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=prjct.location)

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

      db.execute(update(Blueprint).where(
         Blueprint.project==project and Blueprint.host==hostname
         ).values(
         status='30'
         ).execution_options(synchronize_session="fetch"))
      db.commit()

      logger("AMI creation started: "+import_task_id,"info")

      if len(import_task_id) > 0:
         while True:
            response = client.describe_import_image_tasks(
               ImportTaskIds=[
               import_task_id,
               ]
            )
            print(response)
            
            if response['ImportImageTasks'][0]['Status'] == "completed":
               ami_id = import_task_id

               db.execute(update(Blueprint).where(
                  Blueprint.project==project and Blueprint.host==hostname
                  ).values(
                  image_id=ami_id, status='35'
                  ).execution_options(synchronize_session="fetch"))
               db.commit()

               for import_task in response['ImportImageTasks']:
                  for snapshot_detail in import_task['SnapshotDetails']:
                        db.execute(update(Disk).where(
                           Disk.project==project and Disk.host==hostname and Disk.mnt_path==snapshot_detail['UserBucket']['S3Key'].split('-')[1].split('.')[0]
                           ).values(
                           file_size=str(snapshot_detail['DiskImageSize']), disk_id=snapshot_detail['SnapshotId'], vhd=snapshot_detail['UserBucket']['S3Key']
                           ).execution_options(synchronize_session="fetch"))
                        db.commit()
               break
            elif response['ImportImageTasks'][0]['Status'] == "deleted":

               db.execute(update(Blueprint).where(
                  Blueprint.project==project and Blueprint.host==hostname
                  ).values(
                  status='-35'
                  ).execution_options(synchronize_session="fetch"))
               db.commit()

               logger(response['ImportImageTasks'][0]['StatusMessage'], 'error')
               print(response['ImportImageTasks'][0]['StatusMessage'])
               return False
            else:
               await asyncio.sleep(60)
   except Exception as e:
      print(str(e))
      logger("Error while creating AMI:"+str(e),"error")
      
      db.execute(update(Blueprint).where(
         Blueprint.project==project and Blueprint.host==hostname
         ).values(
         status='-35'
         ).execution_options(synchronize_session="fetch"))
      db.commit()

      return False


async def start_ami_creation(project, hostname, db):
   creds.set_aws_creds(project, db)
   hosts = []
   try:
      bucket = db.query(Bucket).filter(Bucket.project==project).first()
      bucket_name = bucket.bucket if bucket is not None else ''

      if hostname == "all":
         hosts = db.query(Blueprint).filter(Blueprint.project==project).all()
      else:
         hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()
   except Exception as e:
      print(repr(e))

   for host in hosts:
      disks = (db.query(Discover).filter(Discover.project==project, Discover.host==host.host).first()).disk_details
      disk_containers = []

      for disk in disks:
         image_name = f'{host.host}{disk["mnt_path"].replace("/", "-slash")}.img'
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
      worker_done = await start_ami_creation_worker(project, disk_containers, hostname, db)
      if worker_done == False:
         return False
   return True