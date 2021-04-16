from model.project import *
from utils.dbconn import *
import os

def set_aws_creds(project):
    try:
        con = create_db_con()
        access_key = Project.objects(name=project)[0]['access_key']
        secret_key = Project.objects(name=project)[0]['secret_key']
        location = Project.objects(name=project)[0]['location']
        credentials_str = '['+project+']\naws_access_key_id = '+ access_key+'\n'+ 'aws_secret_access_key = '+secret_key
        if not os.path.exists('/root/.aws'):
            os.mkdir('/root/.aws')
        with open('/root/.aws/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+project+']\nregion = '+location+'\noutput = json'
        with open('/root/.aws/config', 'w+') as writer:
            writer.write(config_str)
        return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        return False
