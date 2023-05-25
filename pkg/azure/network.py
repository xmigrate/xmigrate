# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from model.blueprint import Blueprint
from model.network import Network, Subnet
from model.project import Project
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
from sqlalchemy import update


def create_vnet(rg_name, vnet_name, cidr, location, project, db):
    ntwrk = db.query(Network).filter(Network.cidr==cidr, Network.project==project).first()
    if not ntwrk.created:
        try:
            prjct = db.query(Project).filter(Project.name==project).first()
            creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
            network_client = NetworkManagementClient(creds, prjct.subscription_id)

            print("Provisioning a vnet...some operations might take a minute or two.")
            poller = network_client.virtual_networks.create_or_update(
                rg_name, vnet_name, {"location": location, "address_space": {"address_prefixes": [cidr]}}
                )
            vnet_result = poller.result()
            print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

            hosts = db.query(Blueprint).filter(Blueprint.network==cidr,Blueprint.project==project).all()
            for host in hosts:
                try:
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host.host
                        ).values(
                        vpc_id=vnet_result.name, status='5'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
                except Exception as e:
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host.host
                        ).values(
                        vpc_id=vnet_result.name, status='-5'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

            db.execute(update(Network).where(
                Network.project==project and Network.cidr==cidr
                ).values(
                created=True, nw_name=vnet_name
                ).execution_options(synchronize_session="fetch"))
            db.commit()

            db.execute(update(Subnet).where(
                Subnet.project==project and Subnet.cidr==cidr and Subnet.nw_name==ntwrk.nw_name
                ).values(
                nw_name=vnet_name
                ).execution_options(synchronize_session="fetch"))
            db.commit()
        except Exception as e:
            print("Vnet creation failed to save: "+repr(e))
            logger("Vnet creation failed to save: "+repr(e),"warning")
            return False
        return True
    else:
        return True


def create_subnet(rg_name, vnet_name, subnet_name, cidr, project, db):
    sbnt = db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==cidr, Subnet.nw_name==vnet_name).first()
    if not sbnt.created:
        prjct = db.query(Project).filter(Project.name==project).first()
        creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
        network_client = NetworkManagementClient(creds, prjct.subscription_id)

        print("Provisioning a subnet...some operations might take a minute or two.")
        poller = network_client.subnets.create_or_update(rg_name, vnet_name, subnet_name, {"address_prefix": cidr})
        subnet_result = poller.result()
        print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
        
        try:
            hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.subnet==cidr).all()
            for host in hosts:
                db.execute(update(Blueprint).where(
                    Blueprint.project==project and Blueprint.host==host.host
                        ).values(
                        subnet_id=str(subnet_result.id), status='10'
                        ).execution_options(synchronize_session="fetch"))
                db.commit()

            db.execute(update(Subnet).where(
                Subnet.project==project and Subnet.cidr==cidr and Subnet.nw_name==vnet_name
                    ).values(
                    created=True, subnet_name=subnet_name
                    ).execution_options(synchronize_session="fetch"))
            db.commit()
        except Exception as e:
            print("Subnet creation failed to save: "+repr(e))
            logger("Subnet creation failed to save: "+repr(e),"warning")
            return False
        return True
    else:
        return True


def create_publicIP(project, rg_name, ip_name, location, subnet_id, host, db):
    print("Provisioning a public IP...some operations might take a minute or two.")
    ip_created = (db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==host).first()).ip_created
    if not ip_created:
        try:
            prjct = db.query(Project).filter(Project.name==project).first()
            creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
            network_client = NetworkManagementClient(creds, prjct.subscription_id)

            poller = network_client.public_ip_addresses.create_or_update(rg_name, ip_name,
                                                                        {
                                                                            "location": location,
                                                                            "sku": {"name": "Standard"},
                                                                            "public_ip_allocation_method": "Static",
                                                                            "public_ip_address_version": "IPV4"
                                                                        }
                                                                        )
            ip_address_result = poller.result()
            print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                ).values(
                ip_created=True, status='15'
                ).execution_options(synchronize_session="fetch"))
            db.commit()
        except Exception as e:
            print("Public IP creation failed: "+repr(e))
            logger("Public IP creation failed: "+repr(e),"warning")

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
        print(f"Provisioned network interface client {nic_result.name}")
        try:
            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                    ).values(
                    nic_id=nic_result.id, ip=ip_address_result.ip_address, status='20'
                    ).execution_options(synchronize_session="fetch"))
            db.commit()
        except Exception as e:
            print("Nework interface creation failed:"+repr(e))
    else:
        logger("Public IP was already created for this host: "+host,"info")
   

async def create_nw(project, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    machines = db.query(Blueprint).filter(Blueprint.project==project).all()
    cidr = []
    subnet = []
    for machine in machines:
        cidr.append(machine.network)
        subnet.append(machine.subnet)
    cidr = list(set(cidr))
    vnet_created = []
    c = 0
    for i in cidr:
        vnet_name = project+"vnet"+str(c)
        vnet_created.append(create_vnet(prjct.resource_group, vnet_name, i, prjct.location, project, db))
        c = c+1
    c = 0
    if True in vnet_created:
        subnet = list(set(subnet))
        subnet_created = []
        for i in subnet:
            subnet_name = project+"subnet"+str(c)
            subnet_created = create_subnet(prjct.resource_group, vnet_name, subnet_name, i, project, db)
        if subnet_created:
            for machine in machines:
                ip_name = machine.host
                subnet_id = machine.subnet_id
                create_publicIP(project, prjct.resource_group, ip_name, prjct.location, subnet_id, machine.host, db)
        else:
            return False
    return True

