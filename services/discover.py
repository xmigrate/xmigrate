from model.discover import Discover
from schemas.discover import DiscoverCreate, DiscoverUpdate
import json
from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import Column
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

    discover = Discover()
    discover_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in discover_data.items():
        if isinstance(value, list):
            value = json.dumps(value)
        setattr(discover, key, value)

    db.add(discover)
    db.commit()
    db.refresh(discover)

    return JSONResponse({"status": 201, "message": "discover data created", "data": [{}]}, status_code=201)


def get_discover(project_id: str, db: Session) -> List[Discover]:
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

    db_discover = get_discover_by_id(data.id, db)
    discover_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in discover_data.items():
        if isinstance(value, list):
            value = json.dumps(value)
        setattr(db_discover, key, value)

    db.add(db_discover)
    db.commit()
    db.refresh(db_discover)

    return JSONResponse({"status": 204, "message": "discover data updated", "data": [{}]}, status_code=204)