from model.project import Project
from model.mapping import Mapper
from model.user import User
from schemas.project import ProjectBase, ProjectUpdate
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from sqlalchemy import update
from sqlalchemy.orm import Session


def check_project_exists(user: str, project: str, db: Session) -> bool:
    '''
    Returns if a project with the given name exists in the current database session for the active user.
    
    :param user: active user
    :param project: project name to check
    :param db: active database session
    '''

    return(db.query(Mapper).join(Project).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).count() > 0)


def create_project(id: str, data: ProjectBase, db: Session) -> JSONResponse:
    '''
    Create a new project with the given details.
    
    :param data: new project details
    :param db: active database session
    '''

    stmt = Project(
        id = id,
        name = data.name,
        provider = data.provider,
        location = data.location,
        aws_access_key = data.aws_access_key,
        aws_secret_key = data.aws_secret_key,
        azure_client_id	= data.azure_client_id,
        azure_client_secret	= data.azure_client_secret,
        azure_tenant_id	= data.azure_tenant_id,
        gcp_service_token = json.dumps(data.gcp_service_token),
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "project created", "data": [{}]})


def get_all_projects(user: str, db: Session) -> list:
    '''
    Returns all active projects associated with the active user.
    
    :param user: active user
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Mapper.is_deleted==False).all())


def get_projectid(user: str, project: str, db: Session) -> str:
    '''
    Returns the id for the specified active project associated with the active user.
    
    :param user: active user
    :param project: project name to retrieve the id from
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).first().id)


def get_project_by_name(user: str, project: str, db: Session) -> Project | None:
    '''
    Returns the specified active project associated with the active user.
    
    :param user: active user
    :param project: project name to check
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).first())


def update_project(project_id: str, data: ProjectUpdate, db: Session) -> JSONResponse:
    '''
    Updates given project with curresponding data.
    
    :param project_id: unique id of the project to update
    :param data: details to update the project with
    :param db: active database session
    '''
    
    stmt = update(Project).where(
        Project.id==project_id and Project.is_deleted==False
    ).values(
        aws_access_key = data.aws_access_key,
        aws_secret_key = data.aws_secret_key,
        azure_client_id = data.azure_client_id,
        azure_client_secret = data.azure_client_secret,
        azure_tenant_id = data.azure_tenant_id,
        gcp_service_token = json.dumps(data.gcp_service_token),
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "project updated", "data": [{}]})