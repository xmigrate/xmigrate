from schemas.project import ProjectBase
from services.project import get_project_by_name
import os
from sqlalchemy.orm import Session


def write_aws_creds(user: str, project: str, db: Session, data: ProjectBase = None) -> None:
    '''
    Configure aws with the given credentials.

    :param user: activer user
    :param project: name of the project
    :param db: active database session
    :param data: project data
    '''

    project = get_project_by_name(user, project, db=db)
    if project is None and data is not None:
        project = data
        
    aws_dir = os.path.expanduser('~/.aws')

    if not os.path.exists(aws_dir):
        os.mkdir(aws_dir)

    with open(f'{aws_dir}/credentials', 'w+') as cred, open(f'{aws_dir}/config', 'w+') as config:
        cred.write(f'[{project.name}]\naws_access_key_id = {project.aws_access_key}\naws_secret_access_key = {project.aws_secret_key}')
        config.write(f'[profile {project.name}]\nregion = {project.location}\noutput = json')