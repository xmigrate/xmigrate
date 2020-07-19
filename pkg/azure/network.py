# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.network import NetworkManagementClient
from utils import dbconn
from model.blueprint import BluePrint
from model.project import Project
import random


def create_vnet(rg_name, vnet_name, cidr, location):
    con = dbconn()
    print("Provisioning a vnet...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
    poller = network_client.virtual_networks.create_or_update(rg_name, vnet_name, {
                                                              "location": location, "address_space": {"address_prefixes": [cidr]}})
    vnet_result = poller.result()
    print(
        "Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")
    try:
        BluePrint.objects(network=cidr).update(vpc_id=vnet_result.name,status='43')
    except:
        print("Vnet creation failed to save")
    finally:
        con.close()
    return True


def create_subnet(rg_name, vnet_name, subnet_name, cidr):
    print("Provisioning a subnet...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
    poller = network_client.subnets.create_or_update(
        rg_name, vnet_name, subnet_name, {"address_prefix": cidr})
    subnet_result = poller.result()
    print(
        "Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
    try:
        BluePrint.objects(subnet=cidr).update(subnet_id=subnet_result.id,status='47')
    except:
        print("Subnet creation failed to save")
    finally:
        con.close()
    return True


async def create_publicIP(project, rg_name, ip_name, location, subnet_id, host):
    print("Provisioning a public IP...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
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
        con = dbconn()
        BluePrint.objects(project=project).update(status='50')
    except:
        print("Public IP creation failed")
    finally:
        con.close()
        
    print("Provisioning a public NIC ...some operations might take a minute or two.")
    poller = network_client.network_interfaces.create_or_update(rg_name,
                                                                nic_name,
                                                                {
                                                                    "location": location,
                                                                    "ip_configurations": [{
                                                                        "name": ip_config_name,
                                                                        "subnet": {"id": subnet_id},
                                                                        "public_ip_address": {"id": ip_address_result.id}
                                                                    }]
                                                                }
                                                                )

    nic_result = poller.result()
    print("Provisioned network interface client {nic_result.name}")
    try:
        con = dbconn()
        BluePrint.objects(project=project,host=host).update(status='53', nic_id=nic_result.id)
    except:
        print("Nework interface creation failed")
    finally:
        con.close()
   

async def create_nw(project):
    con = dbconn()
    rg_name = Project.objects(project=project).to_json()["resource_group"]
    location = Project.objects(project=project).to_json()["location"]
    machines = BluePrint.objects(project=project).to_json()
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
        vnet_created.append(create_vnet(rg_name, vnet_name, i, location))
        c = c+1
    c = 0
    if True in vnet_created:
        subnet = list(set(subnet))
        subnet_created = []
        for i in subnet:
            subnet_name = project+"subnet"+str(c)
            subnet_created = create_subnet(rg_name, vnet_name, subnet_name, i)
        if True in subnet_created:
            machines = BluePrint.objects(project=project).to_json()
            for machine in machines:
                ip_name = machine['host']
                subnet_id = machine['subnet_id'] 
                await(asyncio.create_task(create_publicIP(project, rg_name, ip_name, location, subnet_id,machine['host'])))
    con.close()
    return True

