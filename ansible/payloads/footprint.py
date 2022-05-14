import netifaces
import netaddr
import socket
import psutil
from dotenv import load_dotenv
from os import getenv
# from mongoengine import *
import requests
import json
from mongoengine import StringField
from mongoengine import ListField
from collections import OrderedDict
import sys
import os


niface = 'eth0'

addrs = psutil.net_if_addrs()

for i in addrs.keys():
    if addrs[i][0].address.split('.')[0] in ['192', '172', '10']:
        print(i)
        niface = i

def network_info():
    ifaces = netifaces.interfaces()
    # => ['lo', 'eth0', 'eth1']
    myiface = niface
    addrs = netifaces.ifaddresses(myiface)
    # Get ipv4 stuff
    ipinfo = addrs[socket.AF_INET][0]
    address = ipinfo['addr']
    netmask = ipinfo['netmask']
    # Create ip object and get
    cidr = netaddr.IPNetwork('%s/%s' % (address, netmask))
    # => IPNetwork('192.168.1.150/24')
    network = cidr.network
    # => IPAddress('192.168.1.0')
    fqdn = socket.getfqdn('0.0.0.0')
    resp = {'ip': str(address), 'subnet': str(cidr), 'network': str(network), 'host': fqdn}
    return resp


def disk_info():
    '''
    This function will fetch the disk details and return in this format 
    [{'filesystem': 'ext4', 'disk_size': 8259014656, 'uuid': 'c3d76fc4', 'dev': '/dev/xvda', 'mnt_path': '/'}]
    '''
    root_disk=[]
    dev_names=[]
    for i in psutil.disk_partitions():
        disk_blkid=''
        if 'lv' in i.device:
            continue
        if i.fstype in ['ext4','xfs']:
            if "nvme" not in i.device:
                disk_uuid = os.popen('sudo blkid '+ i.device.rstrip("1234567890")).read()
                for x in disk_uuid.split(" "):
                    if "UUID" in x.upper():
                        disk_blkid = x.split("=")[1].replace('"','')
                disk_size = psutil.disk_usage(i.mountpoint).total
                if len(root_disk)<=0:
                    root_disk.append({"mnt_path":i.mountpoint,"dev":i.device.rstrip('1234567890'),"uuid":disk_blkid,"disk_size":disk_size,"filesystem":i.fstype})
                    dev_names.append(i.device.rstrip('1234567890'))
                elif i.device.rstrip('1234567890') not in dev_names:
                    root_disk.append({"mnt_path":i.mountpoint,"dev":i.device.rstrip('1234567890'),"uuid":disk_blkid,"disk_size":disk_size,"filesystem":i.fstype})
                    dev_names.append(i.device.rstrip('1234567890'))
            else:
                disk_size = psutil.disk_usage(i.mountpoint).total
                disk_uuid = os.popen('sudo blkid '+ i.device[0:-2]).read()
                if len(root_disk)<=0:
                    if len(i.device.split('/')[2]) > 6:
                        root_disk.append({"mnt_path":i.mountpoint,"dev":i.device[0:-2],"uuid":disk_blkid,"disk_size":disk_size,"filesystem":i.fstype})
                        dev_names.append(i.device[0:-2])
                    elif i.device[0:-2] not in dev_names:
                        root_disk.append({"mnt_path":i.mountpoint,"dev":i.device[0:-2],"uuid":disk_blkid,"disk_size":disk_size,"filesystem":i.fstype})
                        dev_names.append(i.device[0:-2])
    return root_disk


def ports_info():
    rows = []
    lc = psutil.net_connections('inet')
    resp = []
    for c in lc:
        (ip, port) = c.laddr
        if ip == '0.0.0.0' or ip == '::':
            if c.type == socket.SOCK_STREAM and c.status == psutil.CONN_LISTEN:
                proto_s = 'tcp'
            elif c.type == socket.SOCK_DGRAM:
                proto_s = 'udp'
            else:
                continue
            pid_s = str(c.pid) if c.pid else '(unknown)'
            pid = c.pid
            pid_name = psutil.Process(pid).name()
            msg = 'PID {} is listening on port {}/{} for all IPs.'
            msg = msg.format(pid_name, port, proto_s)
            resp.append({'name': pid_name, 'port': port, 'type': proto_s})
    return resp


def cpuinfo():
    cpuinfo = OrderedDict()
    procinfo = OrderedDict()
    nprocs = 0
    with open('/proc/cpuinfo') as f:
        for line in f:
            if not line.strip():
                cpuinfo['proc%s' % nprocs] = procinfo
                nprocs = nprocs + 1
                procinfo = OrderedDict()
            else:
                if len(line.split(':')) == 2:
                    procinfo[line.split(':')[0].strip()] = line.split(':')[1].strip()
                else:
                    procinfo[line.split(':')[0].strip()] = ''
    return cpuinfo


def meminfo():
    meminfo = OrderedDict()
    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()
    return meminfo

server_con_string = sys.argv[2]

class Document():
    def __init__(self, *args, **values):
        print(self)

    @classmethod
    def objects(self, **values):
        for key in values:
            setattr(self, key, values[key])
        return self

    @classmethod
    def update(self, **kwargs):
        url = server_con_string+"/master/status/update"
        jsonObj = {}
        for i in dir(self):
            if i.startswith('_'):
                continue
            jsonObj[i] = getattr(self, i)
            if(str(getattr(self, i)).startswith('<')):
                jsonObj[i] = None    
        data = {
            'classObj': jsonObj,
            'classType': self.__name__,
            'data': kwargs
        }
        headers = {'Accept-Encoding': 'UTF-8', 'Content-Type': 'application/json', 'Accept': '*/*'}
        req = requests.post(url, data=json.dumps(data),headers=headers)
        print(req.text)
        return self

class Discover(Document):
    host = StringField(required=True, max_length=200 )
    ip = StringField(required=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    project = StringField(required=True, max_length=50)
    public_ip = StringField(required=True, max_length=150)
    disk_details = ListField()
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

def main():
    db_con_string = sys.argv[2]
    project = sys.argv[1]
    public_ip = sys.argv[3]
    # con = connect(host=db_con_string)
    result = network_info()
    result['ports'] = ports_info()
    cores = str(len(cpuinfo().keys()))
    cpu_model = cpuinfo()['proc0']['model name']
    ram = meminfo()['MemTotal']
    try:
        Discover.objects(project=project,host=socket.gethostname()).update(host=socket.gethostname(),public_ip=public_ip, ip=result['ip'], subnet=result['subnet'], network=result['network'],
                 ports=result['ports'], cores=cores, cpu_model=cpu_model, ram=ram, disk_details=disk_info(), upsert=True)
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
    # finally:
        # con.shutdown()


if __name__ == '__main__':
    main()
