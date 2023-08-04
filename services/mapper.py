from model.mapping import Mapper
from datetime import datetime
from sqlalchemy.orm import Session


def create_mapping(user_id: str, project_id: str, db: Session) -> None:
    '''
    Map the created projects with the specified user.
    
    :param user_id: unique id of the user
    :param project_id: unique id of the project
    :param db: active database session
    '''

    stmt = Mapper(
        user = user_id,
        project = project_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)