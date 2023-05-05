async def read_logs(project_name):
    l = ''
    f = open('./logs/ansible/{}/gather_facts_log.txt'.format(project_name), 'r')
    l = f.read()
    return l

def read_migration_logs():
    l = ''
    f = open('./logs/ansible/migration_log.txt','r')
    l = f.read()
    return l