
from google.oauth2 import service_account
from googleapiclient import discovery
from utils.logger import *

def login_using_service_account(service_account_json):
    credentials = service_account.Credentials.from_service_account_info(service_account_json)
    return credentials

def get_service_compute_v1(service_account_json):
    credentials = login_using_service_account(service_account_json)
    return discovery.build('compute', 'v1', credentials=credentials)