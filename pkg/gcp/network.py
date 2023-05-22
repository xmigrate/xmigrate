from .gcp import get_service_compute_v1
from .gcp import REGIONS
from exception.exception import GcpRegionNotFound
from model.blueprint import Blueprint
from model.project import Project
from model.network import Subnet
from utils.logger import *
import asyncio
from sqlalchemy import update
from typing import List


def list_vpc(project_id, service_account_json) -> List[str]:
    service = get_service_compute_v1(service_account_json)
    request = service.networks().list(project=project_id)
    res = []
    while request is not None:
        response = request.execute()
        for network in response['items']:
            res.append(network)
        request = service.networks().list_next(
            previous_request=request, previous_response=response)
    return res


def get_vpc(project_id, service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    request = service.networks().get(project=project_id, network=network_name)
    response = request.execute()
    return response


async def create_vpc(project_id, service_account_json, network_name, wait_for_creation=False):
    service = get_service_compute_v1(service_account_json)
    network_body = {
        "name": network_name,
        "autoCreateSubnetworks": False,
    }
    request = service.networks().insert(project=project_id, body=network_body)
    response = request.execute()
    if wait_for_creation:
        while True:
            result = service.globalOperations().get(project=project_id, operation=response['name']).execute()
            if result['status'] == 'DONE':
                print("done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result
            await asyncio.sleep(1)
    return response


def delete_vpc(project_id, service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    request = service.networks().delete(project=project_id, network=network_name)
    return request.execute()


def list_subnet(project_id, service_account_json, network_name, region):
    if region not in REGIONS:
        raise GcpRegionNotFound(region)
    network = get_vpc(project_id, service_account_json, network_name)
    service = get_service_compute_v1(service_account_json)
    request = service.subnetworks().list(project=project_id, region=region)
    res = []
    while request is not None:
        response = request.execute()
        for subnetwork in response['items']:
            if network["selfLink"] == subnetwork["network"]:
                res.append(subnetwork)
        request = service.subnetworks().list_next(
            previous_request=request, previous_response=response)
    return res


def get_subnet(project_id, service_account_json, subnet_name, region):
    service = get_service_compute_v1(service_account_json)
    request = service.subnetworks().get(project=project_id, region=region, subnetwork=subnet_name)
    response = request.execute()
    return response


def create_subnet(project_id, service_account_json, network_name, region, name, cidr):
    if region not in REGIONS:
        raise GcpRegionNotFound(region)
    service = get_service_compute_v1(service_account_json)
    network = get_vpc(project_id, service_account_json, network_name)
    subnetwork_body = {
        "name": name,
        "network": network["selfLink"],
        "ipCidrRange": cidr
    }
    request = service.subnetworks().insert(
        project=project_id, region=region, body=subnetwork_body)
    response = request.execute()
    return response


async def create_nw(project, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    machines = db.query(Blueprint).filter(Blueprint.project==project).all()

    vpc = []
    subnet = []
    for machine in machines:
        vpc.append(machine.network)
        subnet.append(machine.subnet)

    vpc = list(set(vpc))
    vpc_created = []
    
    for network_name in vpc:
        print("Provisioning a vpc...some operations might take a minute or two.")
        created = (db.query(Subnet).filter(Subnet.project==project, Subnet.nw_name==network_name).first()).created
        if not created:
            try:
                res = await create_vpc(prjct.gcp_project_id, prjct.service_account, network_name, True)
                hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==network_name).all()
                for host in hosts:
                    try:
                        db.execute(update(Blueprint).where(
                            Blueprint.project==project and Blueprint.host==host.host
                            ).values(
                            vpc_id=res['targetLink'], status='10'
                            ).execution_options(synchronize_session="fetch"))
                        db.commit()
                    except Exception as e:
                        db.execute(update(Blueprint).where(
                            Blueprint.project==project and Blueprint.host==host.host
                            ).values(
                            vpc_id=res, status='-10'
                            ).execution_options(synchronize_session="fetch"))
                        db.commit()
                db.execute(update(Subnet).where(
                    Subnet.project==project and Subnet.nw_name==network_name
                    ).values(
                    created=True
                    ).execution_options(synchronize_session="fetch"))
                db.commit()
            except Exception as e:
                print("Vnet creation failed to save: "+repr(e))
                logger("Vnet creation failed to save: "+repr(e), "warning")
                vpc_created.append(False)
            vpc_created.append(True)
        else:
            vpc_created.append(True)
    c = 0
    if False in vpc_created:
        return False
    else:
        subnet = list(set(subnet))
        subnet_created = []
        for i in subnet:
            print("Provisioning a subnet...some operations might take a minute or two.")
            sbnt = db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==i).first()
            if not sbnt.created:
                try:
                    subnet_name = project+"subnet"+str(c)
                    subnet_result = create_subnet(prjct.gcp_project_id, prjct.service_account ,network_name, prjct.location, subnet_name, i)
                    hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.subnet==i).all()
                    for host in hosts:
                        try:
                            db.execute(update(Blueprint).where(
                                Blueprint.project==project and Blueprint.host==host.host
                                ).values(
                                subnet_id=str(subnet_result['targetLink']), status='20'
                                ).execution_options(synchronize_session="fetch"))
                            db.commit()
                        except Exception as e:
                            db.execute(update(Blueprint).where(
                                Blueprint.project==project and Blueprint.host==host.host
                                ).values(
                                subnet_id=str(subnet_result['targetLink']), status='-20'
                                ).execution_options(synchronize_session="fetch"))
                            db.commit()        
                    subnet_name = sbnt.subnet_name
                    db.execute(update(Subnet).where(
                        Subnet.project==project and Subnet.cidr==i and Subnet.subnet_name==subnet_name
                        ).values(
                        created=True
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
                except Exception as e:
                    print("Subnet creation failed to save: "+repr(e))
                    logger("Subnet creation failed to save: "+repr(e), "warning")
                    subnet_created.append(False) 
                subnet_created.append(True) 
            else:
                subnet_created.append(True) 
        if False in subnet_created:
            return False
    return True
