from datetime import datetime, timedelta
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas

def generate_sas_token(storage_account,access_key):
    sas_token = generate_account_sas(
            storage_account,
            account_key=access_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=2)
        )
    return sas_token