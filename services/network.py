from model.network import Network, Subnet
from schemas.network import NetworkCreate, NetworkUpdate, SubnetCreate, SubnetUpdate
from datetime import datetime
from typing import List, Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
from sqlalchemy.orm import Session


def check_network_exists(blueprint_id: str, cidr: str, name: str, db: Session) -> bool:
    '''
    Returns if network data with given cidr already exists in the current project blueprint.
    
    :param blueprint_id: id of the corresponding bluerpint
    :param cidr: cidr of the network
    :param name: name of the network
    :param db: active database session
    '''

    return(db.query(Network).filter(Network.blueprint==blueprint_id, Network.cidr==cidr, Network.is_deleted==False).count() > 0 or
           db.query(Network).filter(Network.blueprint==blueprint_id, Network.name==name, Network.is_deleted==False).count() > 0)


def check_subnet_exists(network_id: str, cidr: str, name: str, db: Session) -> bool:
    '''
    Returns if subnet data with given cidr already exists in the given network.
    
    :param network_id: id of the corresponding network
    :param cidr: cidr of the subnet
    :param name: name of the subnet
    :param db: active database session
    '''

    return(db.query(Subnet).filter(Subnet.network==network_id, Subnet.cidr==cidr, Subnet.is_deleted==False).count() > 0 or
           db.query(Subnet).filter(Subnet.network==network_id, Subnet.subnet_name==name, Subnet.is_deleted==False).count() > 0)


def create_network(data: NetworkCreate, db: Session) -> JSONResponse:
    '''
    Saves the network data for the given blueprint.

    :param data: network data to save
    :param db: active database session
    '''

    network = Network()
    network_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in network_data.items():
        setattr(network, key, value)

    db.add(network)
    db.commit()
    db.refresh(network)

    return JSONResponse({"status": 201, "message": "network data created", "data": [{}]}, status_code=201)


def create_subnet(data: SubnetCreate, db: Session) -> JSONResponse:
    '''
    Saves the subnet data for the given network.

    :param data: subnet data to save
    :param db: active database session
    '''

    subnet = Subnet()
    subnet_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in subnet_data.items():
        setattr(subnet, key, value)

    db.add(subnet)
    db.commit()
    db.refresh(subnet)

    return JSONResponse({"status": 201, "message": "subnet data created", "data": [{}]}, status_code=201)


def delete_network(blueprint_id: str, name: str, db: Session) -> JSONResponse:
    '''
    Deletes a network.

    :param blueprint_id: id of the corresponding bluerpint
    :param name: name of the network
    :param db: active database session
    '''

    stmt = update(Network).where(
       Network.blueprint==blueprint_id and
       Network.name==name and
       Network.is_deleted==False
    ).values(
        is_deleted = True,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "network data deleted", "data": [{}]})


def delete_all_subnets(network_id: str, db: Session) -> JSONResponse:
    '''
    Deletes all subnets in a network.

    :param network_id: id of the corresponding network
    :param db: active database session
    '''

    stmt = update(Subnet).where(
       Subnet.network==network_id and
       Subnet.is_deleted==False
    ).values(
        is_deleted = True,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "all subnet data in the network deleted", "data": [{}]})


def delete_subnet(network_id: str, name: str, db: Session) -> JSONResponse:
    '''
    Deletes a subnet.

    :param network_id: id of the corresponding network
    :param name: name of the subnet
    :param db: active database session
    '''

    stmt = update(Subnet).where(
       Subnet.network==network_id and
       Subnet.subnet_name==name and
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


def get_networkid_by_name(name: str, blueprint_id: str, db: Session) -> Column[str]:
    '''
    Returns the id of a network.

    :param name: name of the network
    :param blueprint_id: id of the corresponding bluerpint
    :param db: active database session
    '''
    return(db.query(Network).filter(Network.name==name, Network.blueprint==blueprint_id, Network.is_deleted==False).first().id)


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

    db_network = get_network_by_id(data.id, db)
    network_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in network_data.items():
        setattr(db_network, key, value)

    db.add(db_network)
    db.commit()
    db.refresh(db_network)

    return JSONResponse({"status": 204, "message": "network data updated", "data": [{}]}, status_code=204)


def update_subnet(data: SubnetUpdate, db: Session) -> JSONResponse:
    '''
    Update a subnet data.
    
    :param data: subnet update data
    :param db: active database session
    '''

    db_subnet = get_subnet_by_id(data.id, db)
    subnet_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in subnet_data.items():
        setattr(db_subnet, key, value)

    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)

    return JSONResponse({"status": 204, "message": "subnet data updated", "data": [{}]}, status_code=204)