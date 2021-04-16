import boto3

def get_locations(access_key,secret_key):
    regions = []
    try:
        client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name='us-east-1')
        regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
        return regions,True 
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        return regions, False