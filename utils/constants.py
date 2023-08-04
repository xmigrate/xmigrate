from enum import Enum


class Provider(Enum):
    AWS = 'aws'
    AZURE = 'azure'
    GCP = 'gcp'


class Test(Enum):
    HEADER = "Xm-test"