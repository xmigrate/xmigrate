# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from schemas.machines import VMUpdate
from schemas.network import NetworkUpdate, SubnetUpdate
from schemas.project import ProjectUpdate
from services.blueprint import get_blueprintid
from services.machines import get_all_machines, update_vm
from services.network import get_all_networks, get_all_subnets, update_network, update_subnet
from services.project import get_project_by_name, update_project
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from sqlalchemy import update

def create_rg(resource_client, project, db):
    try:
        if project.azure_resource_group is not None and project.azure_resource_group_created:
            return True
    except Exception as e:
        print("Reaching Project document failed: "+ str(e))
        logger("Reaching Project document failed: "+ str(e), "warning")
    else:
        try:
            print("Provisioning a resource group...some operations might take a minute or two.")
            rg_result = resource_client.resource_groups.create_or_update(project.azure_resource_group, {"location": project.location})
            print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region.")

            project_data = ProjectUpdate(project_id=project.id, azure_resource_group_created=True)
            update_project(project_data, db)
            return True
        except Exception as e:
            print("Resource group creation failed "+str(e))
            logger("Resource group creation failed: "+repr(e),"warning")
            return False
        

def create_vnet(network_client, project, network, machine, update_host, db) -> bool:
    try:
        print("Provisioning a vnet...some operations might take a minute or two.")
        poller = network_client.virtual_networks.create_or_update(
            project.azure_resource_group, network.name, {"location": project.location, "address_space": {"address_prefixes": [network.cidr]}}
            )
        vnet_result = poller.result()
        print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

        network_data = NetworkUpdate(network_id=network.id, target_network_id=vnet_result.name, created=True)
        update_network(network_data, db)
        if update_host:
            vm_data = VMUpdate(machine.id, status=5)
            update_vm(vm_data, db)
    except Exception as e:
        if update_host:
            vm_data = VMUpdate(machine.id, status=-5)
            update_vm(vm_data, db)
        print("Vnet creation failed to save: "+ str(e))
        logger("Vnet creation failed to save: "+ str(e),"warning")
        return False
    return True


def create_subnet(network_client, project, network, subnet, machine, update_host, db) -> bool:
    try:
        print("Provisioning a subnet...some operations might take a minute or two.")
        poller = network_client.subnets.create_or_update(project.azure_resource_group, network.name, subnet.subnet_name, {"address_prefix": subnet.cidr})
        subnet_result = poller.result()
        print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

        subnet_data = SubnetUpdate(subnet_id=subnet.id, target_subnet_id=str(subnet_result.id), created=True)
        update_subnet(subnet_data, db)
        if update_host:
            vm_data = VMUpdate(machine.id, status=10)
            update_vm(vm_data, db)
    except Exception as e:
        print("Subnet creation failed to save: "+ str(e))
        logger("Subnet creation failed to save: "+ str(e),"warning")
        return False
    return True


def create_publicIP(network_client, project, subnet, machine, update_host, db):
    try:
        poller = network_client.public_ip_addresses.create_or_update(project.azure_resource_group, machine.hostname,
                                                                    {
                                                                        "location": project.loaction,
                                                                        "sku": {"name": "Standard"},
                                                                        "public_ip_allocation_method": "Static",
                                                                        "public_ip_address_version": "IPV4"
                                                                    }
                                                                )
        ip_address_result = poller.result()
        print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

        if update_host:
            vm_data = VMUpdate(machine_id=machine.id, ip_created=True, status=15)
            update_vm(vm_data, db)
    except Exception as e:
        print("Public IP creation failed: "+ str(e))
        logger("Public IP creation failed: "+ str(e),"warning")
    else:
        try:
            print("Provisioning a public NIC ...some operations might take a minute or two.")
            poller = network_client.network_interfaces.create_or_update(project.azure_resource_group, machine.hostname,
                                                                        {
                                                                            "location": project.loaction,
                                                                            "ip_configurations": [{
                                                                                "name": machine.hostname,
                                                                                "subnet": {"id": subnet.target_suvnet_id},
                                                                                "public_ip_address": {"id": ip_address_result.id}
                                                                            }]
                                                                        }
                                                                    )

            nic_result = poller.result()
            print(f"Provisioned network interface client {nic_result.name}")
            if update_host:
                vm_data = VMUpdate(machine_id=machine.id, nic_id=nic_result.id, ip=ip_address_result.ip_address, status=20)
                update_vm(vm_data, db)
        except Exception as e:
            print("Nework interface creation failed:"+ str(e))
   

async def create_nw(user, project, db):
    try:
        project = get_project_by_name(user, project, db)
        blueprint_id = get_blueprintid(project.id, db)
        machines = get_all_machines(blueprint_id, db)

        creds = ServicePrincipalCredentials(client_id=project.azure_client_id, secret=project.azure_client_secret, tenant=project.azure_tenant_id)
        resource_client = ResourceManagementClient(creds, project.azure_subscription_id)
        rg_created = create_rg(resource_client, project, db)

        if rg_created:
            network_client = NetworkManagementClient(creds, project.azure_subscription_id)
            for machine in machines:
                networks = get_all_networks(blueprint_id, db)
                for network in networks:
                    vnet_created = network.created
                    subnets = get_all_subnets(network.id, db)
                    update_host = True if network.cidr == machine.network else False
                    if network.target_network_id is None and not vnet_created:
                        vnet_created = create_vnet(network_client, project, network, machine, update_host, db)
                    if vnet_created:
                        for subnet in subnets:
                            if not subnet.created and vnet_created:
                                subnet_created = create_subnet(network_client, project, network, subnet, machine, update_host, db)
                                if subnet_created and not machine.ip_created:
                                    create_publicIP(network_client, project, subnet, machine, update_host, db)
    except Exception as e:
        print(repr(e))
        return False
    return True