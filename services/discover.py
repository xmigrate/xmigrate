from model.discover import Discover
from utils.id_gen import unique_id_gen
from datetime import datetime
import json
from sqlalchemy import update
from sqlalchemy.orm import Session


def check_discover_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if discover data already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).count() > 0)


def create_discover(data: tuple, db: Session) -> None:
    '''
    Saves the discover data for the project.
    
    :param data: source vm details
    :param db: active database session
    '''

    project_id, hostname, network, subnet, ports, cpu_core, cpu_model, ram, disk_details, ip = data

    stmt = Discover(
        id = unique_id_gen("discover"),
        project = project_id,
        hostname = hostname,
        network = network,
        subnet = subnet,
        ports = ports,
        cpu_core = cpu_core,
        cpu_model = cpu_model,
        ram = ram,
        disk_details = json.dumps(disk_details),
        ip = ip,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)


def get_discover(project_id: str, db: Session):
    '''
    Returns the discover data for the poject.
    
    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).all())


def get_discoverid(project_id: str, db: Session) -> str:
    '''
    Returns the id for the discover data of the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).first().id)


def update_discover(discover_id: str, data: tuple, db: Session) -> None:
    '''
    Updates the discover data for the project.
    
    :param discover_id: unique id of the existing discover data
    :param data: source vm details
    :param db: active database session
    '''
    
    _, hostname, network, subnet, ports, cpu_core, cpu_model, ram, disk_details, ip = data

    stmt = update(Discover).where(
        Discover.id==discover_id and Discover.is_deleted==False
    ).values(
        hostname = hostname,
        subnet = subnet,
        network = network,
        ports = ports,
        cpu_core = cpu_core,
        cpu_model = cpu_model,
        ram = ram,
        disk_details = json.dumps(disk_details),
        ip = ip,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()