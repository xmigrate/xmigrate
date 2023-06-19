from model.nodes import Nodes
from schemas.node import NodeCreate, NodeUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
import json
from sqlalchemy import update
from sqlalchemy.orm import Session


def check_node_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if node data already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Nodes).filter(Nodes.project==project_id, Nodes.is_deleted==False).count() > 0)


def create_node(data: NodeCreate, db: Session) -> None:
    '''
    Creates node data for the project.
    
    :param data: ansible target node data
    :param db: active database session
    '''

    hosts = {'hosts': data.hosts}

    stmt = Nodes(
        id = unique_id_gen("node"),
        hosts = json.dumps(hosts),
        username = data.username,
        password = data.password,
        project = data.project_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)


def get_nodeid(project_id: str, db: Session) -> str:
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


def update_node(data: NodeUpdate, db: Session) -> None:
    '''
    Updates the node data for the project.
    
    :param data: ansible target node data
    :param db: active database session
    '''

    hosts = {'hosts': data.hosts}
    
    stmt = update(Nodes).where(
        Nodes.id==data.node_id and Nodes.is_deleted==False
    ).values(
        hosts = json.dumps(hosts),
        username = data.username,
        password = data.password,
        updated_at = datetime.now()
    )

    db.execute(stmt)
    db.commit()