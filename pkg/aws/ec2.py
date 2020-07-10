
def create_machine(subnet_id,ami_id,machine_type):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')
    amiid = ami_id
    filters = [{'Name':'name','Values':[ami_id]}]
    response = client.describe_images(Filters=filters)
    ami_id = response['Images'][0]['ImageId']
    instances = ec2.create_instances(ImageId=ami_id, InstanceType=machine_type, MaxCount=1, MinCount=1, NetworkInterfaces=[{'SubnetId': subnet_id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True}])
    instances[0].wait_until_running()
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    BluePrint.objects(ami_id=amiid).update(instance_id=instances[0].id)
    BluePrint.objects(ami_id=amiid).update(status='Build completed')
    con.close()
