from model.blueprint import Blueprint
from utils.id_gen import unique_id_gen
from datetime import datetime
from sqlalchemy.orm import Session


def check_blueprint_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if a blueprint already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Blueprint).filter(Blueprint.project==project_id, Blueprint.is_deleted==False).count() > 0)


def create_blueprint(project_id: str, db: Session) -> None:
    '''
    Create a blueprint for the project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    stmt = Blueprint(
        id = unique_id_gen("blueprint"),
        project = project_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)


def get_blueprint(project_id: str, db: Session):
    '''
    Returns the blueprint data for the poject.
    
    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Blueprint).filter(Blueprint.project==project_id, Blueprint.is_deleted==False).first())


def get_blueprintid(project_id: str, db: Session) -> str:
    '''
    Returns the id of the blueprint associated with the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Blueprint).filter(Blueprint.project==project_id, Blueprint.is_deleted==False).first().id)