from model.disk import Disk
from utils.id_gen import unique_id_gen
from datetime import datetime
from sqlalchemy.orm import Session


def check_disk_exists(blueprint_id: str, mnt_path: str, db: Session) -> bool:
    '''
    Returns if a disk data already exists for the given blueprint.
    
    :param blueprint_id: id of the corresponding blueprint
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.blueprint==blueprint_id, Disk.mnt_path==mnt_path, Disk.is_deleted==False).count() > 0)


def create_disk(data: tuple, db: Session) -> None:
    '''
    Store the disk details.
    
    :param data: details of the disk
    :param db: active database session
    '''
    
    host, vhd, file_size, mnt_path, disk_clone, blueprint_id = data

    stmt = Disk(
        id = unique_id_gen("Disk"),
        host = host,
        vhd = vhd,
        file_size = file_size,
        mnt_path = mnt_path,
        disk_clone = disk_clone,
        blueprint = blueprint_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)