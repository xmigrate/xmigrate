from mongoengine import *


class Disk(Document):
    host = StringField(required=True, max_length=150)
    vhd = StringField(required=True)
    file_size = StringField(required=True)
    project = StringField(required=True, max_length=150)
    mnt_path = StringField(required=True, max_length=150)
    disk_id = StringField(required=True, max_length=550)
    meta = {
        'indexes': [
            {'fields': ('host', 'project', 'mnt_path'), 'unique': True}
        ]
    }