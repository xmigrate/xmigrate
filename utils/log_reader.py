async def read_logs(curr_working_dir, project_name):
    l = ''
    f = open('{}/logs/ansible/{}/log.txt'.format(curr_working_dir ,project_name),'r')
    l = f.read()
    return l

def read_migration_logs():
    l = ''
    f = open('./logs/ansible/migration_log.txt','r')
    l = f.read()
    return l