def read_logs():
    l = ''
    f = open('./logs/ansible/log.txt','r')
    l = f.read()
    return l
