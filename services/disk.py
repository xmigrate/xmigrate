from model.disk import Disk
from schemas.disk import DiskCreate, DiskUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session


def check_disk_exists(vm_id: str, mountpoint: str, db: Session) -> bool:
    '''
    Returns if a disk data already exists for the host.
    
    :param vm_id: id of the corresponding host
    :param mountpoint: mount path of the disk
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.vm==vm_id, Disk.mnt_path==mountpoint, Disk.is_deleted==False).count() > 0)


def create_disk(data: DiskCreate, db: Session) -> None:
    '''
    Store the disk details.
    
    :param data: details of the disk
    :param db: active database session
    '''

    stmt = Disk(
        id = unique_id_gen("Disk"),
        host = data.hostname,
        mnt_path = data.mnt_path,
        vm = data.machine_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)


def get_all_disks(vm_id: str, db: Session) -> str:
    '''
    Returns the disk data of all disks for the host.

    :param vm_id: id of the corresponding host
    :param db: active database session
    '''
    return(db.query(Disk).filter(Disk.vm==vm_id, Disk.is_deleted==False).first().id)


def get_diskid(vm_id: str, mountpoint: str, db: Session) -> str:
    '''
    Returns the id of a partciular disk data for the host.

    :param vm_id: id of the corresponding host
    :param mountpoint: mount path of the disk
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.mnt_path==mountpoint, Disk.vm==vm_id, Disk.is_deleted==False).first().id)


def update_disk(data: DiskUpdate, db: Session) -> None:
    stmt = update(Disk).where(
        Disk.id==data.disk_id and Disk.is_deleted==False
    ).values(
        host = data.hostname,
        mnt_path = data.mnt_path,
        vm = data.machine_id,
        vhd = data.vhd,
        file_size = data.file_size,
        disk_clone = data.disk_clone,
        target_disk_id = data.target_disk_id,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()