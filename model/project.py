from mongoengine import *


class GcpServiceAccount:
    type: StringField(max_length=150)
    project_id: StringField(max_length=150)
    private_key_id: StringField(max_length=150)
    private_key: StringField(max_length=3000)
    client_email: StringField(max_length=150)
    client_id: StringField(max_length=150)
    auth_uri: StringField(max_length=150)
    token_uri: StringField(max_length=150)
    auth_provider_x509_cert_url: StringField(max_length=150)
    client_x509_cert_url: StringField(max_length=150)

class Project(Document):
    provider = StringField(required=True, max_length=20)
    location = StringField(required=True)
    name = StringField(required=True, max_length=50,unique=True)
    resource_group = StringField(max_length=100)
    subscription_id = StringField(max_length=100)
    client_id = StringField(max_length=150)
    secret = StringField(max_length=150)
    tenant_id = StringField(max_length=150)
    users = ListField(required=True) 
    access_key = StringField(max_length=150)
    secret_key = StringField(max_length=150)
    resource_group_created = BooleanField(default=False)
    username = StringField(max_length=150)
    password = StringField(max_length=150)
    public_ip = ListField()
    service_account = GcpServiceAccount
    gcp_project_id = StringField(max_length=150)