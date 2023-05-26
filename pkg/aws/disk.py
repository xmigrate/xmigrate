from model.blueprint import Blueprint
from model.storage import Bucket
from model.discover import Discover
from model.project import Project
import os
from ansible_runner import run_async

async def start_cloning(project, hostname, db):
    bkt = db.query(Bucket).filter(Bucket.project==project).first()
    prjct = db.query(Project).filter(Project.name==project).first()
    public_ip = (db.query(Discover).filter(Discover.project==project, Discover.host==hostname).first()).public_ip
    server = os.getenv('BASE_URL')
    current_dir = os.getcwd()

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, prjct.provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project)
    extravars = {
        'bucket': bkt.bucket,
        'access_key': bkt.access_key,
        'secret_key': bkt.secret_key,
        'server': server,
        'project': project,
        'ansible_user': prjct.username
    }
    envvars = {
        'ANSIBLE_BECOME_USER': prjct.username,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir ,project)
    }

    cloned = await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, limit=public_ip, quiet=True)

    if (not (bool(cloned[1].stats['failures']) or bool(cloned[1].stats['dark']))):
        machines = db.query(Blueprint).filter(Blueprint.project==project).all()
        machine_count = db.query(Blueprint).filter(Blueprint.project==project).count()
        flag = True
        status_count = 0
        while flag:
            for machine in machines:
                if int(machine.status)>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
        return not flag
    else:
        return False