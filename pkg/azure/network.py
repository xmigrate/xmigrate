# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.network import NetworkManagementClient
from utils.dbconn import *
from model.blueprint import BluePrint
from model.project import Project
from model.network import *
import random
from azure.common.credentials import ServicePrincipalCredentials
from utils.logger import *

def create_vnet(rg_name, vnet_name, cidr, location, project):
    print("Provisioning a vnet...some operations might take a minute or two.")
    con = create_db_con()
    created = Network.objects(cidr=cidr, project=project)[0]['created']
    if not created:
        client_id = Project.objects(name=project)[0]['client_id']
        secret = Project.objects(name=project)[0]['secret']
        tenant_id = Project.objects(name=project)[0]['tenant_id']
        subscription_id = Project.objects(name=project)[0]['subscription_id']
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
        network_client = NetworkManagementClient(creds,subscription_id)
        poller = network_client.virtual_networks.create_or_update(rg_name, vnet_name, {
                                                                "location": location, "address_space": {"address_prefixes": [cidr]}})
        vnet_result = poller.result()
        print(
            "Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")
        try:
            BluePrint.objects(network=cidr, project=project).update(vpc_id=vnet_result.name,status='43')
            Network.objects(cidr=cidr, project=project).update(created=True, upsert=True)
        except Exception as e:
            print("Vnet creation failed to save: "+repr(e))
            logger("Vnet creation failed to save: "+repr(e),"warning")
            return False
        finally:
            con.close()
        return True
    else:
        return True


def create_subnet(rg_name, vnet_name, subnet_name, cidr, project):
    print("Provisioning a subnet...some operations might take a minute or two.")
    con = create_db_con()
    created = Subnet.objects(cidr=cidr, project=project)[0]['created']
    if not created:
        client_id = Project.objects(name=project)[0]['client_id']
        secret = Project.objects(name=project)[0]['secret']
        tenant_id = Project.objects(name=project)[0]['tenant_id']
        subscription_id = Project.objects(name=project)[0]['subscription_id']
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
        network_client = NetworkManagementClient(creds,subscription_id)
        con.close()
        poller = network_client.subnets.create_or_update(
            rg_name, vnet_name, subnet_name, {"address_prefix": cidr})
        subnet_result = poller.result()
        print(
            "Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
        try:
            con = create_db_con()
            print(subnet_result.id)
            BluePrint.objects(subnet=cidr).update(subnet_id=str(subnet_result.id),status='60')
            Subnet.objects(cidr=cidr, project=project).update(created=True, upsert=True)
        except Exception as e:
            print("Subnet creation failed to save: "+repr(e))
            logger("Subnet creation failed to save: "+repr(e),"warning")
            return False
        finally:
            con.close()
        return True
    else:
        return True


def create_publicIP(project, rg_name, ip_name, location, subnet_id, host):
    print("Provisioning a public IP...some operations might take a minute or two.")
    con = create_db_con()
    ip_created = BluePrint.objects(project=project, host=host)[0]['ip_created']
    if not ip_created:
        client_id = Project.objects(name=project)[0]['client_id']
        secret = Project.objects(name=project)[0]['secret']
        tenant_id = Project.objects(name=project)[0]['tenant_id']
        subscription_id = Project.objects(name=project)[0]['subscription_id']
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
        network_client = NetworkManagementClient(creds,subscription_id)
        con.close()
        poller = network_client.public_ip_addresses.create_or_update(rg_name, ip_name,
                                                                    {
                                                                        "location": location,
                                                                        "sku": {"name": "Standard"},
                                                                        "public_ip_allocation_method": "Static",
                                                                        "public_ip_address_version": "IPV4"
                                                                    }
                                                                    )

        ip_address_result = poller.result()
        print(
            "Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")
        try:
            con = create_db_con()
            BluePrint.objects(project=project, host=host).update(status='60', ip_created=True)
        except Exception as e:
            print("Public IP creation failed: "+repr(e))
            logger("Public IP creation failed: "+repr(e),"warning")
        finally:
            con.close()
        print("Provisioning a public NIC ...some operations might take a minute or two.")
        poller = network_client.network_interfaces.create_or_update(rg_name,
                                                                    host,
                                                                    {
                                                                        "location": location,
                                                                        "ip_configurations": [{
                                                                            "name": host,
                                                                            "subnet": {"id": subnet_id},
                                                                            "public_ip_address": {"id": ip_address_result.id}
                                                                        }]
                                                                    }
                                                                    )

        nic_result = poller.result()
        print("Provisioned network interface client {nic_result.name}")
        try:
            con = create_db_con()
            BluePrint.objects(project=project,host=host).update(status='60', nic_id=nic_result.id)
        except Exception as e:
            print("Nework interface creation failed:"+repr(e))
        finally:
            con.close()
    else:
        logger("Public IP was already created for this host: "+host,"info")
   

async def create_nw(project,hostname):
    con = create_db_con()
    rg_name = Project.objects(name=project)[0]["resource_group"]
    location = Project.objects(name=project)[0]["location"]
    machines = BluePrint.objects(project=project, host=hostname)
    cidr = []
    subnet = []
    for machine in machines:
        cidr.append(machine['network'])
        subnet.append(machine['subnet'])
    cidr = list(set(cidr))
    vnet_created = []
    c = 0
    for i in cidr:
        vnet_name = project+"vnet"+str(c)
        vnet_created.append(create_vnet(rg_name, vnet_name, i, location, project))
        c = c+1
    c = 0
    if True in vnet_created:
        subnet = list(set(subnet))
        subnet_created = []
        for i in subnet:
            subnet_name = project+"subnet"+str(c)
            subnet_created = create_subnet(rg_name, vnet_name, subnet_name, i, project)
        if subnet_created:
            machines = BluePrint.objects(project=project)
            for machine in machines:
                ip_name = machine['host']
                subnet_id = machine['subnet_id'] 
                create_publicIP(project, rg_name, ip_name, location, subnet_id,machine['host'])
        else:
            con.close()
            return False
    con.close()
    return True

