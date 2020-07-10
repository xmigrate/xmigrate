def read_logs():
    l = ''
    f = open('./ansible/log.txt','r')
    l = f.read()
    return l
