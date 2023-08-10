from utils.logger import Logger
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.subscription import SubscriptionClient

async def get_locations(subscription_id, client_id, secret, tenant_id):
    available_locations = []
    try:
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
        subscription_client = SubscriptionClient(creds)
        locations = subscription_client.subscriptions.list_locations(subscription_id)
        
        for location in locations:
            available_locations.append(location.name)
        return available_locations, True 
    except Exception as e:
        Logger.warning("Fetching available locations failed: %s" %(str(e)))
        return available_locations, False