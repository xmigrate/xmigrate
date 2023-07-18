from pkg.aws.aws_config import write_aws_creds
from routes.auth import TokenData, get_current_user
from schemas.project import ProjectBase, ProjectUpdate
from services.mapper import create_mapping
from services.project import (check_project_exists, create_project, get_all_projects, get_project_by_name, get_projectid, update_project)
from services.user import get_userid
from test_header_files.test_data import project_test_data
from utils.constants import Provider
from utils.database import dbconn
from utils.id_gen import unique_id_gen
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.post('/project')
async def project_create(data: ProjectBase, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        test_header = request.headers.get('Xm-test')
        if test_header == "test":
            data = await project_test_data(current_user['username'], data, db)
                      
        project_exists = check_project_exists(current_user['username'], data.name, db)
        if not project_exists:
            if data.provider == Provider.AWS.value:
                write_aws_creds(current_user['username'], data.name, db, data)
            
            project_id = unique_id_gen(data.name)
            project_created = create_project(project_id, data, db)
            if project_created is not None:
                user_id = get_userid(current_user['username'], db)
                create_mapping(user_id, project_id, db)
                return project_created
        else:
            return jsonable_encoder({"message": f"project {data.name} already exists for the user!"})
    except Exception as e:
        print(str(e))
        if "IntegrityError" in str(type(e)):
            raise ValueError("Unsupported Provider")
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "project creation failed!"}))     


@router.get('/project')
async def project_get(name: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    if name == "all":
        return get_all_projects(current_user['username'], db)
    else:
        return get_project_by_name(current_user['username'], name, db)


@router.post('/project/update')
async def project_update(data: ProjectUpdate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.name, db)
        return update_project(project_id, data, db)
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "Couldn't update project!"})) 