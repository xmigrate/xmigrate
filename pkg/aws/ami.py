import os, sys, time
from mongoengine import *
from model.blueprint import *
from utils.dbconn import *
from model.storage import Bucket
from model.project import *
import asyncio
from pkg.aws import creds
import boto3
from utils.logger import *

async def start_ami_creation_worker(bucket_name, image_name, project):
   con = create_db_con()
   access_key = Project.objects(name=project)[0]['access_key']
   secret_key = Project.objects(name=project)[0]['secret_key']
   region = Project.objects(name=project)[0]['location']
   import_task_id = ''
   client = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
   file_trust_policy='''{
       "Version":"2012-10-17",
       "Statement":[
          {
             "Sid":"",
             "Effect":"Allow",
             "Principal":{
                "Service":"vmie.amazonaws.com"
             },
             "Action":"sts:AssumeRole",
             "Condition":{
                "StringEquals":{
                   "sts:ExternalId":"vmimport"
                }
             }
          }
       ]
    }'''
   try:
      response = client.create_role(RoleName='vmimport',AssumeRolePolicyDocument=file_trust_policy,Description='For vm migration',MaxSessionDuration=7200,Tags=[{'Key': 'app','Value': 'xmigrate'},])
      file_role_policy = '''{
         "Version":"2012-10-17",
         "Statement":[
            {
               "Effect":"Allow",
               "Action":[
                  "s3:ListBucket",
                  "s3:GetBucketLocation"
               ],
               "Resource":[
                  "arn:aws:s3:::'''+bucket_name+'''"
               ]
            },
            {
               "Effect":"Allow",
               "Action":[
                  "s3:GetObject"
               ],
               "Resource":[
                  "arn:aws:s3:::'''+bucket_name+'''/*"
               ]
            },
            {
               "Effect":"Allow",
               "Action":[
                  "ec2:ModifySnapshotAttribute",
                  "ec2:CopySnapshot",
                  "ec2:RegisterImage",
                  "ec2:Describe*"
               ],
               "Resource":"*"
            }
         ]
      }'''
      response = client.put_role_policy(
         RoleName='vmimport',
         PolicyName='vmimport',
         PolicyDocument=file_role_policy
      )
   except Exception as e:
      print(str(e))
   client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name=region)
   response = client.import_image(
      DiskContainers=[
         {
               'Description': 'Xmigrate',
               'Format': 'RAW',
               'UserBucket': {
                  'S3Bucket': bucket_name,
                  'S3Key': image_name
               }
         },
      ],
      TagSpecifications=[
        {
            'ResourceType': 'import-image-task',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': image_name
                },
            ]
        },
    ]
   )
   try:
      import_task_id = response['ImportTaskId']
      BluePrint.objects(host=image_name.replace('.img','')).update(status='30')
      logger("AMI creation started: "+import_task_id,"info")
   except Exception as e:
      print(str(e))
      logger("Error while creating AMI:"+str(e),"error")
   if len(import_task_id) > 0:
      while True:
         response = client.describe_import_image_tasks(
            ImportTaskIds=[
            import_task_id,
            ]
         )
         if response['ImportImageTasks'][0]['Status'] == "completed":
            ami_id = import_task_id
            BluePrint.objects(host=image_name.replace('.img','')).update(image_id=ami_id)
            BluePrint.objects(host=image_name.replace('.img','')).update(status='35')
            break
         else:
            asyncio.sleep(60)
   con.close()


async def start_ami_creation(project):
   set_creds = creds.set_aws_creds(project)
   con = create_db_con()
   bucket_name = ''
   images = []
   try:
      bucket = Bucket.objects(project=project)[0]
      images = BluePrint.objects(project=project)
      bucket_name = bucket['bucket']
   except Exception as e:
      print(repr(e))
      logger(str(e),"warning")
   finally:
      con.close()
   for image in images:
      image_name = image['host']+'.img'
      await start_ami_creation_worker(bucket_name, image_name, project)
   return True