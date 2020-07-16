def read_logs():
    l = ''
    f = open('./logs/ansible/log.txt','r')
    l = f.read()
    return l

def read_migration_logs():
    l = ''
    f = open('./logs/ansible/migration_log.txt','r')
    l = f.read()
    return l