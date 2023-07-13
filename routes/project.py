from pkg.aws.aws_config import write_aws_creds
from routes.auth import TokenData, get_current_user
from schemas.project import ProjectBase, ProjectUpdate
from services.mapper import create_mapping
from services.project import (check_project_exists, create_project, get_all_projects, get_project_by_name, get_projectid, update_project)
from services.user import get_userid
from utils.constants import Provider
from utils.database import dbconn
from utils.id_gen import unique_id_gen
from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import json, os


router = APIRouter()

@router.post('/project')
async def project_create(data: ProjectBase, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        test_header = request.headers.get('X-test')
        if test_header == "test" :


            json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_data.json')
            with open(json_file_path, 'r') as json_file:
                test_data = json.load(json_file)
            project_exists = check_project_exists(current_user['username'], data.name, db)
            if not project_exists:
                
                #filling dummy data if any field comes empty for test case
                '''if data.provider is None:
                    data.provider = "aws"
                test = dict(data)
                print(test)
                for key in test.keys():
                    if test[key] is None:
                        test[key] = test_data[key]
                
                data=ProjectBase.parse_obj(test)
                print(data)
               
               '''
                if data.provider == "aws":
                    if data.aws_access_key is None:
                        data.aws_access_key = test_data["aws_access_key"]
                    if data.aws_secret_key is None:
                        data.aws_secret_key = test_data["aws_secret_key"]
                    write_aws_creds(current_user['username'], data.name, db, data)
                
                if data.provider == "azure":
                    if data.azure_client_id is None:
                        data.azure_client_id = test_data["azure_client_id"]
                    if data.azure_client_secret is None:
                        data.azure_client_secret = test_data["azure_client_secret"]
                    if data.azure_tenant_id is None:
                        data.azure_tenant_id = test_data["azure_tenant_id"]
                    if data.azure_subscription_id is None:
                        data.azure_subscription_id = test_data["azure_subscription_id"]
                    if data.azure_resource_group is None:
                        data.azure_resource_group = test_data["azure_resource_group"]
                    if data.azure_resource_group_created is None:
                        data.azure_resource_group_created = test_data["azure_resource_group_created"]

                if data.provider == "gcp":
                    if data.gcp_service_token is None:
                        data.gcp_service_token = test_data["gcp_service_token"]
                      
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