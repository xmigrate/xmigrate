from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns


class BluePrint(Model):
    host = columns.Text(primary_key=True, max_length=200)
    ip = columns.Text(required=True)
    ip_created = columns.Boolean(required=True, default=False)
    subnet = columns.Text(required=True, max_length=50)
    network = columns.Text(required=True, max_length=50)
    ports = columns.List(value_type=columns.Map(key_type=columns.Text(),value_type=columns.Text()))
    cores = columns.Text(max_length=2)
    cpu_model = columns.Text(required=True, max_length=150)
    ram = columns.Text(required=True, max_length=50)
    machine_type = columns.Text(required=True, max_length=150)
    status = columns.Text(required=False, max_length=100)
    image_id = columns.Text(required=False, max_length=500)
    vpc_id = columns.Text(required=False, max_length=100)
    subnet_id = columns.Text(required=False, max_length=200)
    public_route = columns.Boolean(required=False)
    ig_id = columns.Text(required=False, max_length=100)
    route_table = columns.Text(required=False, max_length=100)
    vm_id = columns.Text(required=False, max_length=200)
    project = columns.Text(primary_key=True, max_length=50)
    nic_id = columns.Text(max_length=200)
    disk_clone = columns.List(value_type=columns.Map(key_type=columns.Text(),value_type=columns.Text()))




class BluePrintMongo(Document):
    host = StringField(required=True, max_length=200)
    ip = StringField(required=True)
    ip_created = BooleanField(required=True, default=False)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    machine_type = StringField(required=True, max_length=150)
    status = StringField(required=False, max_length=100)
    image_id = StringField(required=False, max_length=500)
    vpc_id = StringField(required=False, max_length=100)
    subnet_id = StringField(required=False, max_length=200)
    public_route = BooleanField(required=False)
    ig_id = StringField(required=False, max_length=100)
    route_table = StringField(required=False, max_length=100)
    vm_id = StringField(required=False, max_length=200)
    project = StringField(required=True, max_length=50)
    nic_id = StringField(max_length=200)
    disk_clone = ListField()
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }


