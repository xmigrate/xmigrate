from utils.dbconn import *
from model.blueprint import *
from model.network import *

def fetch_hosts(project):
    try:
        con = create_db_con()
        response = {}
        sub_hosts = {}
        hosts = BluePrint.objects(project=project)
        for host in hosts:
            sub_name = Subnet.objects(project=project,cidr=host['subnet'])
            sub_hosts[sub_name['subnet_name']].append(host)
        for subnet in sub_hosts.keys():
            nw_name = Subnet.objects(project=project,subnet_name=subnet)
            response[nw_name['nw_name']].append(sub_hosts[subnet])
            con.close()
        return response
    except Exception as e:
        print("Reading from db failed: "+str(e))
        con.close()
        return {"msg":"Failed fetching details"}


