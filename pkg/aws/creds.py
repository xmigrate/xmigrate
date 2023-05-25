from model.project import Project
import os

def set_aws_creds(project, db):
    try:
        prjct = db.query(Project).filter(Project.name==project).first()
        aws_dir = os.path.expanduser("~/.aws")

        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)
            
        with open(f'{aws_dir}/credentials', 'w+') as cred, open(f'{aws_dir}/config', 'w+') as config:
            cred.write(f'[{project}]\naws_access_key_id = {prjct.access_key}\naws_secret_access_key = {prjct.secret_key}')
            config.write(f'[profile {project}]\nregion = {prjct.location}\noutput = json')
        return True
    except Exception as e:
        print(repr(e))
        return False
