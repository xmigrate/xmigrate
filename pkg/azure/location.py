from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.subscription import SubscriptionClient
from utils.logger import *

def get_locations(subscription_id,client_id,secret,tenant_id):
    available_locations = []
    try:
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
        subscription_client = SubscriptionClient(creds)
        locations = subscription_client.subscriptions.list_locations(subscription_id)
        for location in locations:
            available_locations.append(location.name)
        return available_locations,True 
    except Exception as e:
        print(repr(e))
        logger("Fetching available locations failed: "+str(e),"warning")
        return available_locations, False