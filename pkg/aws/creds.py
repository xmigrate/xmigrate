from model.project import *
from utils.dbconn import *
import os

def set_aws_creds(project):
    try:
        con = create_db_con()
        access_key = Project.objects(name=project)[0]['access_key']
        secret_key = Project.objects(name=project)[0]['secret_key']
        location = Project.objects(name=project)[0]['location']
        aws_dir = os.path.expanduser("~/.aws/")
        credentials_str = '['+project+']\naws_access_key_id = '+ access_key+'\n'+ 'aws_secret_access_key = '+secret_key
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)
        with open(aws_dir+'/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+project+']\nregion = '+location+'\noutput = json'
        with open(aws_dir+'/config', 'w+') as writer:
            writer.write(config_str)
        return True
    except Exception as e:
        print(repr(e))
        return False
