from model.nodes import Nodes
from schemas.node import NodeCreate, NodeUpdate
import json
from typing import Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column
from sqlalchemy.orm import Session


def check_node_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if node data already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.project==project_id, Nodes.is_deleted==False).count() > 0)


def create_node(data: NodeCreate, db: Session) -> JSONResponse:
    '''
    Creates node data for the project.
    
    :param data: ansible target node data
    :param db: active database session
    '''

    nodes = Nodes()
    node_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in node_data.items():
        setattr(nodes, key, value)

    db.add(nodes)
    db.commit()
    db.refresh(nodes)

    return JSONResponse({"status": 201, "message": "node data created", "data": [{}]}, status_code=201)


def get_nodeid(project_id: str, db: Session) -> Column[str]:
    '''
    Returns the id for the node data of the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.project==project_id, Nodes.is_deleted==False).first().id)


def get_nodes(project_id: str, db: Session) -> Union[Nodes, None]:
    '''
    Returns the node data for the poject.
    
    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.project==project_id, Nodes.is_deleted==False).first())


def get_node_by_id(node_id: str, db: Session) -> Nodes:
    '''
    Returns the node data for the poject.
    
    :param node_id: unique id of the node data
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.id==node_id).first())


def update_node(data: NodeUpdate, db: Session) -> JSONResponse:
    '''
    Updates the node data for the project.
    
    :param data: ansible target node data
    :param db: active database session
    '''

    db_node = get_node_by_id(data.id, db)
    node_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in node_data.items():
        if isinstance(value, list):
            value = json.dumps(value)
        setattr(db_node, key, value)

    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    return JSONResponse({"status": 204, "message": "node data updated", "data": [{}]}, status_code=204)