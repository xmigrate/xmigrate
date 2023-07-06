from model.network import Network, Subnet
from schemas.network import NetworkCreate, NetworkUpdate, SubnetCreate, SubnetUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
from typing import List, Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
from sqlalchemy.orm import Session


def check_network_exists(blueprint_id: str, cidr: str, db: Session) -> bool:
    '''
    Returns if network data with given cidr already exists in the current project blueprint.
    
    :param blueprint_id: id of the corresponding bluerpint
    :param cidr: cidr of the network
    :param db: active database session
    '''

    return(db.query(Network).filter(Network.blueprint==blueprint_id, Network.cidr==cidr, Network.is_deleted==False).count() > 0)


def check_subnet_exists(network_id: str, cidr: str, db: Session) -> bool:
    '''
    Returns if subnet data with given cidr already exists in the given network.
    
    :param network_id: id of the corresponding network
    :param cidr: cidr of the subnet
    :param db: active database session
    '''

    return(db.query(Subnet).filter(Subnet.network==network_id, Subnet.cidr==cidr, Subnet.is_deleted==False).count() > 0)


def create_network(blueprint_id: str, data: NetworkCreate, db: Session) -> JSONResponse:
    '''
    Saves the network data for the given blueprint.

    :param blueprint_id: id of the corresponding blueprint
    :param data: network data to save
    :param db: active database session
    '''

    stmt = Network(
        id = unique_id_gen(data.cidr),
        blueprint = blueprint_id,
        name = data.name,
        cidr = data.cidr,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "network data created", "data": [{}]})


def create_subnet(network_id: str, data: SubnetCreate, db: Session) -> JSONResponse:
    '''
    Saves the subnet data for the given network.

    :param network_id: id of the corresponding network
    :param data: subnet data to save
    :param db: active database session
    '''

    stmt = Subnet(
        id = unique_id_gen(data.cidr),
        network = network_id,
        subnet_name = data.name,
        cidr = data.cidr,
        subnet_type = data.nw_type,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "subnet data created", "data": [{}]})


def delete_network(blueprint_id: str, cidr: str, db: Session) -> JSONResponse:
    '''
    Deletes a network.

    :param blueprint_id: id of the corresponding bluerpint
    :param cidr: cidr of the network
    :param db: active database session
    '''

    stmt = update(Network).where(
       Network.blueprint==blueprint_id and
       Network.cidr==cidr and
       Network.is_deleted==False
    ).values(
        is_deleted = True,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "network data deleted", "data": [{}]})


def delete_subnet(network_id: str, cidr: str, db: Session) -> JSONResponse:
    '''
    Deletes a subnet.

    :param network_id: id of the corresponding network
    :param cidr: cidr of the subnet
    :param db: active database session
    '''

    stmt = update(Subnet).where(
       Subnet.network==network_id and
       Subnet.cidr==cidr and
       Subnet.is_deleted==False
    ).values(
        is_deleted = True,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "subnet data deleted", "data": [{}]})


def get_all_networks(blueprint_id: str, db: Session) -> List[Network]:
    '''
    Returns all networks defined in a blueprint.

    :param blueprint_id: id of the corresponding bluerpint
    :param db: active database session
    '''

    return(db.query(Network).filter(Network.blueprint==blueprint_id, Network.is_deleted==False).all())


def get_all_subnets(network_id: str, db: Session) -> List[Subnet]:
    '''
    Returns all subnets defined in a network.

    :param network_id: id of the corresponding network
    :param db: active database session
    '''

    return(db.query(Subnet).filter(Subnet.network==network_id, Subnet.is_deleted==False).all())


def get_networkid(cidr: str, blueprint_id: str, db: Session) -> Column[str]:
    '''
    Returns the id of a network.

    :param cidr: cidr of the network
    :param blueprint_id: id of the corresponding bluerpint
    :param db: active database session
    '''
    return(db.query(Network).filter(Network.cidr==cidr, Network.blueprint==blueprint_id, Network.is_deleted==False).first().id)


def get_network_by_cidr(cidr: str, blueprint_id: str, db: Session) -> Union[Network, None]:
    '''
    Returns a network from the blueprint.
    
    :param cidr: cidr of the network
    :param blueprint_id: id of the corresponding bluerpint
    :param db: active database session
    '''

    return(db.query(Network).filter(Network.cidr==cidr, Network.blueprint==blueprint_id, Network.is_deleted==False).first())


def get_network_by_id(network_id: str, db: Session) -> Network:
    '''
    Returns a network from the blueprint.
    
    :param network_id: id of the corresponding network
    :param db: active database session
    '''

    return(db.query(Network).filter(Network.id==network_id).first())


def get_subnet_by_cidr(cidr: str, network_id: str, db: Session) -> Union[Subnet, None]:
    '''
    Returns a subnet from the network.
    
    :param cidr: cidr of the network
    :param network: id of the corresponding network
    :param db: active database session
    '''
    return(db.query(Subnet).filter(Subnet.cidr==cidr, Subnet.network==network_id, Subnet.is_deleted==False).first())


def get_subnet_by_id(subnet_id: str, db: Session) -> Subnet:
    '''
    Returns a subnet from the network.
    
    :param subnet_id: id of the corresponding subnet
    :param db: active database session
    '''
    
    return(db.query(Subnet).filter(Subnet.id==subnet_id).first())


def update_network(data: NetworkUpdate, db: Session) -> JSONResponse:
    '''
    Update a network data.
    
    :param data: network update data
    :param db: active database session
    '''

    network_data = get_network_by_id(data.network_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            data_dict[key] = network_data[key]
    data = NetworkUpdate.parse_obj(data_dict)

    stmt = update(Network).where(
        Network.id==data.network_id and Network.is_deleted==False
    ).values(
        target_network_id = data.target_network_id,
        ig_id = data.ig_id,
        route_table = data.route_table,
        created =  data.created,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "network data updated", "data": [{}]})


def update_subnet(data: SubnetUpdate, db: Session) -> JSONResponse:
    '''
    Update a subnet data.
    
    :param data: subnet update data
    :param db: active database session
    '''

    subnet_data = get_subnet_by_id(data.subnet_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            data_dict[key] = subnet_data[key]
    data = SubnetUpdate.parse_obj(data_dict)

    stmt = update(Subnet).where(
        Subnet.id==data.subnet_id and Subnet.is_deleted==False
    ).values(
        target_subnet_id = data.target_subnet_id,
        created =  data.created,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "subnet data updated", "data": [{}]})