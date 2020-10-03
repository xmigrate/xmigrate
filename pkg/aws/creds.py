import pexpect
from model.project import *
from utils.dbconn import *

def set_aws_creds(project):
    try:
        con = create_db_con()
        access_key = Project.objects(name=project)[0]['access_key']
        secret_key = Project.objects(name=project)[0]['secret_key']
        location = Project.objects(name=project)[0]['location']
        child = pexpect.spawn('aws configure --profile '+project)
        child.expect ('AWS Access Key ID *')
        child.sendline (access_key)
        child.expect ('AWS Secret Access Key*')
        child.sendline (secret_key)
        child.expect ('Default region name*')
        child.sendline (location)
        child.expect ('Default output format*')
        child.sendline ('json\n')
        return True
    except Expection as e:
        print(repr(e))
        return False
