
from google.oauth2 import service_account
from googleapiclient import discovery
from utils.logger import *

REGIONS = [
    "us-central1",
    "europe-west1",
    "us-west1",
    "asia-east1",
    "us-east1",
    "asia-northeast1",
    "asia-southeast1",
    "us-east4",
    "australia-southeast1",
    "europe-west2",
    "europe-west3",
    "southamerica-east1",
    "asia-south1",
    "northamerica-northeast1",
    "europe-west4",
    "europe-north1",
    "us-west2",
    "asia-east2",
    "europe-west6",
    "asia-northeast2",
    "asia-northeast3",
    "us-west3",
    "us-west4",
    "asia-southeast2",
    "europe-central2",
    "northamerica-northeast2",
    "asia-south2",
    "australia-southeast2",
    "southamerica-west1",
    "us-east7"
]


def login_using_service_account(service_account_json):
    credentials = service_account.Credentials.from_service_account_info(
        service_account_json)
    return credentials


def get_service_compute_v1(service_account_json):
    credentials = login_using_service_account(service_account_json)
    return discovery.build('compute', 'v1', credentials=credentials)

def get_service_cloudtasks_v2(service_account_json):
    credentials = service_account.Credentials.from_service_account_info(
        service_account_json)
    return discovery.build('cloudtasks', 'v2', credentials=credentials)
