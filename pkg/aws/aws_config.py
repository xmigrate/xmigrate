import os

def write_aws_creds(project: str, access_key: str, secret_key: str, location: str) -> None:
    '''
    Configure aws with the given credentials.

    :param project: name of the project
    :param access_key: aws access key
    :param secret_key: aws secret access key
    :param location: aws region
    '''

    aws_dir = os.path.expanduser('~/.aws')

    if not os.path.exists(aws_dir):
        os.mkdir(aws_dir)

    with open(f'{aws_dir}/credentials', 'w+') as cred, open(f'{aws_dir}/config', 'w+') as config:
        cred.write(f'[{project}]\naws_access_key_id = {access_key}\naws_secret_access_key = {secret_key}')
        config.write(f'[profile {project}]\nregion = {location}\noutput = json')