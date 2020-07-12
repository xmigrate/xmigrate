# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.network import NetworkManagementClient


def create_vnet(rg_name, vnet_name, cidr, location):
    print(f"Provisioning a vnet...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
    poller = network_client.virtual_networks.create_or_update(rg_name, vnet_name, {
                                                              "location": location, "address_space": {"address_prefixes": [cidr]}})
    vnet_result = poller.result()
    print(
        f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")
    return True


def create_subnet(rg_name, vnet_name, subnet_name, cidr):
    print(f"Provisioning a subnet...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
    poller = network_client.subnets.create_or_update(
        rg_name, vnet_name, subnet_name, {"address_prefix": cidr})
    subnet_result = poller.result()
    print(
        f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
    return subnet_result, True


def create_publicIP(rg_name, ip_name, location):
    print(f"Provisioning a public IP...some operations might take a minute or two.")
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
        f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")
    return ip_address_result, True


def create_nw_interface(rg_name, nic_name, location, ip_config_name, subnet_result, ip_address_result):
    print(f"Provisioning a public NIC ...some operations might take a minute or two.")
    network_client = get_client_from_cli_profile(NetworkManagementClient)
    poller = network_client.network_interfaces.create_or_update(rg_name,
                                                                nic_name,
                                                                {
                                                                    "location": location,
                                                                    "ip_configurations": [{
                                                                        "name": ip_config_name,
                                                                        "subnet": {"id": subnet_result.id},
                                                                        "public_ip_address": {"id": ip_address_result.id}
                                                                    }]
                                                                }
                                                                )

    nic_result = poller.result()
    print(f"Provisioned network interface client {nic_result.name}")
    return nic_result, True
