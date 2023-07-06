from model.disk import Disk
from schemas.disk import DiskCreate, DiskUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
import json
from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
from sqlalchemy.orm import Session


def check_disk_exists(vm_id: str, mountpoint: str, db: Session) -> bool:
    '''
    Returns if a disk data already exists for the host.
    
    :param vm_id: id of the corresponding host
    :param mountpoint: mount path of the disk
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.vm==vm_id, Disk.mnt_path==mountpoint, Disk.is_deleted==False).count() > 0)


def create_disk(data: DiskCreate, db: Session) -> JSONResponse:
    '''
    Store the disk details.
    
    :param data: details of the disk
    :param db: active database session
    '''

    stmt = Disk(
        id = unique_id_gen("Disk"),
        hostname = data.hostname,
        mnt_path = data.mnt_path,
        vm = data.vm_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "disk data created", "data": [{}]})


def get_all_disks(vm_id: str, db: Session) -> List[Disk]:
    '''
    Returns the disk data of all disks for the host.

    :param vm_id: id of the corresponding host
    :param db: active database session
    '''
    return(db.query(Disk).filter(Disk.vm==vm_id, Disk.is_deleted==False).all())


def get_diskid(vm_id: str, mountpoint: str, db: Session) -> Column[str]:
    '''
    Returns the id of a partciular disk data for the host.

    :param vm_id: id of the corresponding host
    :param mountpoint: mount path of the disk
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.mnt_path==mountpoint, Disk.vm==vm_id, Disk.is_deleted==False).first().id)


def get_disk_by_id(disk_id: str, db: Session) -> Disk:
    '''
    Returns the disk data of the specified disk for the host.

    :param disk_id: id of the corresponding disk
    :param db: active database session
    '''

    return(db.query(Disk).filter(Disk.id==disk_id).first())


def update_disk(data: DiskUpdate, db: Session) -> JSONResponse:
    '''
    Update the disk details.
    
    :param data: details of the disk
    :param db: active database session
    '''

    disk_data = get_disk_by_id(data.disk_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            if key == 'disk_clone' and disk_data[key] is not None:
                data_dict[key] = json.loads(disk_data[key])
            else:
                table_key = key.rstrip('_id') if 'vm' in key else key
                data_dict[key] = disk_data[table_key]
    data = DiskUpdate.parse_obj(data_dict)

    stmt = update(Disk).where(
        Disk.id==data.disk_id and Disk.is_deleted==False
    ).values(
        hostname = data.hostname,
        mnt_path = data.mnt_path,
        vm = data.vm_id,
        vhd = data.vhd,
        file_size = data.file_size,
        disk_clone = json.dumps(data.disk_clone),
        target_disk_id = data.target_disk_id,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "disk data updated", "data": [{}]})