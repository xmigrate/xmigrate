from model.nodes import Nodes
from schemas.node import NodeCreate, NodeUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
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

    stmt = Nodes(
        id = unique_id_gen("node"),
        hosts = json.dumps(data.hosts),
        username = data.username,
        password = data.password,
        project = data.project_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "node data created", "data": [{}]})


def get_nodeid(project_id: str, db: Session) -> Column[str]:
    '''
    Returns the id for the node data of the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.project==project_id, Nodes.is_deleted==False).first().id)


def get_nodes(project_id: str, db: Session) -> Nodes | None:
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

    node_data = get_node_by_id(data.node_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            if key == 'hosts':
                data_dict[key] = json.loads(node_data[key])
            else:
                data_dict[key] = node_data[key.rstrip('_id')]
    data = NodeUpdate.parse_obj(data_dict)
    
    stmt = update(Nodes).where(
        Nodes.id==data.node_id and Nodes.is_deleted==False
    ).values(
        hosts = json.dumps(data.hosts),
        username = data.username,
        password = data.password,
        updated_at = datetime.now()
    )

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "node data updated", "data": [{}]})