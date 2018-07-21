import pexpect, os, sys, time
from mongoengine import *

class BluePrint(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    machine_type = StringField(required=True, max_length=150)
    status = StringField(required=False, max_length=100)
    ami_id = StringField(required=False, max_length=100)


def start_ami_creation(bucket_name,nsg_filename):
    file_trust_policy = open('trust-policy.json', 'w')
    s='''{
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
    file_trust_policy.write(s)
    file_trust_policy.close()
    pexpect.run('aws iam create-role --role-name vmimport --assume-role-policy-document file://trust-policy.json') 
    file_role_policy = open('role-policy.json', 'w')
    s='''{
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
    file_role_policy.write(s)
    file_role_policy.close()
    pexpect.run('aws iam put-role-policy --role-name vmimport --policy-name vmimport --policy-document file://role-policy.json')
    file_containers = open('containers.json', 'w')
    s='''[{
        "Description": "BlueThroat-Build",
        "Format": "raw",
        "UserBucket": {
            "S3Bucket": "'''+bucket_name+'''",
            "S3Key": "'''+nsg_filename+'''"
        }
    }]'''
    file_containers.write(s)
    file_containers.close()
    output = pexpect.run('aws ec2 import-image --description "NSG-Build" --disk-containers file://containers.json')
    start='ImportTaskId": "'
    try:
        amiid = (output.split(start))[1].split('"')[0]
    except:
        print output
        print start
    print '1) Remove the temp files (trust-policy.json, role-policy.json, containers.json)'
    pexpect.run('rm trust-policy.json')
    pexpect.run('rm role-policy.json')
    pexpect.run('rm containers.json')

    print '2) Check the status of loading the AMI image to your EC2. This usually takes 20-30 minutes'
    while not "success" in output:
        progress_output = pexpect.run('aws ec2 describe-import-image-tasks --import-task-ids %s' % amiid)
        con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
        time.sleep(120) # delays for 120 seconds
        progress_start='Progress": "'
        BluePrint.objects(host=nsg_filename.replace('.img','')).update(status='Started conversion')
        if progress_start in progress_output:
            progress = (progress_output.split(progress_start))[1].split('"')[0]
            BluePrint.objects(host=nsg_filename.replace('.img','')).update(status=progress)
            print '    The progress on importing the image to EC2 is: "'+progress+'%"'
            print progress_output
        if "completed" in progress_output:
            output = "success"
            BluePrint.objects(host=nsg_filename.replace('.img','')).update(status='Completed conversion')
    print '***********************************************************'
    print '***     Image has been successfully imported to EC2     ***'
    print '***********************************************************'
    print amiid
    BluePrint.objects(host=nsg_filename.replace('.img','')).update(ami_id=amiid)
    con.close()


