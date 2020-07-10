import netifaces
import netaddr
import socket
import psutil
from dotenv import load_dotenv
from os import getenv
from mongoengine import *
from collections import OrderedDict

niface = 'eth0'

load_dotenv()

db_con_string = getenv("DB")

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
  root_disk =''
  for i in psutil.disk_partitions():
    if i.mountpoint == '/':
      root_disk = i.device.rstrip('1234567890')
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


class Post(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    disk = StringField(required=True, max_length=50)


def main():
    con = connect(host=db_con_string)
    result = network_info()
    result['ports'] = ports_info()
    cores = str(len(cpuinfo().keys()))
    disk = disk_info()
    cpu_model = cpuinfo()['proc0']['model name']
    ram = meminfo()['MemTotal']
    post1 = Post(host=result['host'], ip=result['ip'], subnet=result['subnet'], network=result['network'],
                 ports=result['ports'], cores=cores, cpu_model=cpu_model, ram=ram, disk=disk_info())
    try:
        post1.save()
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
    finally:
        con.close()


if __name__ == '__main__':
    main()
