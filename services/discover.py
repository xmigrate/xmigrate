from model.discover import Discover
from schemas.discover import DiscoverCreate, DiscoverUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
from sqlalchemy.orm import Session


def check_discover_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if discover data already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).count() > 0)


def create_discover(data: DiscoverCreate, db: Session) -> JSONResponse:
    '''
    Saves the discover data for the project.
    
    :param data: source vm details
    :param db: active database session
    '''

    stmt = Discover(
        id = unique_id_gen("discover"),
        project = data.project_id,
        hostname = data.hostname,
        network = data.network,
        subnet = data.subnet,
        ports = data.ports,
        cpu_core = data.cpu_core,
        cpu_model = data.cpu_model,
        ram = data.ram,
        disk_details = json.dumps(data.disk_details),
        ip = data.ip,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "discover data created", "data": [{}]})


def get_discover(project_id: str, db: Session) -> list[Discover]:
    '''
    Returns the discover data for the poject.
    A project can have only one entry for discover but it is returned as a list to avoid parsing error in frontend in case of null data.
    
    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).all())


def get_discoverid(project_id: str, db: Session) -> Column[str]:
    '''
    Returns the id for the discover data of the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Discover).filter(Discover.project==project_id, Discover.is_deleted==False).first().id)


def get_discover_by_id(discover_id: str, db: Session) -> Discover:
    '''
    Returns the discover data for the poject.
    
    :param discover_id: unique id of the discover data
    :param db: active database session
    '''
    
    return(db.query(Discover).filter(Discover.id==discover_id).first())


def update_discover(data: DiscoverUpdate, db: Session) -> JSONResponse:
    '''
    Updates the discover data for the project.
    
    :param data: source vm details
    :param db: active database session
    '''

    discover_data = get_discover_by_id(data.discover_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            if key == 'disk_details':
                data_dict[key] = json.loads(discover_data[key])
            else:
                data_dict[key] = discover_data[key.rstrip('_id')]
    data = DiscoverUpdate.parse_obj(data_dict)

    stmt = update(Discover).where(
        Discover.id==data.discover_id and Discover.is_deleted==False
    ).values(
        hostname = data.hostname,
        network = data.network,
        subnet = data.subnet,
        ports = data.ports,
        cpu_core = data.cpu_core,
        cpu_model = data.cpu_model,
        ram = data.ram,
        disk_details = json.dumps(data.disk_details),
        ip = data.ip,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "discover data updated", "data": [{}]})