from __main__ import app
from utils.dbconn import *
from model.discover import *
from quart import jsonify
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/start/building', methods=['POST','GET'])
@jwt_required
def start_building():
    con = create_db_con()
    machines = json.loads(BluePrint.objects.to_json())
    vpcs = []
    subnets = []
    for machine in machines:
      vpc = machine['network']
      subnet = machine['subnet']
      ami_id = machine['ami_id']
      hostname = machine['host']
      public_route = machine['public_route']
      if vpc not in  vpcs:
        try:
          build_vpc(vpc,public_route)
          vpcs.append(vpc)
          BluePrint.objects(network=vpc).update(status='VPC created')
        except Exception as e:
          print("Something went wrong while creating vpc: "+str(e))
          logger(str(e),"warning")
    machines = json.loads(BluePrint.objects.to_json())
    for machine in machines:
      subnet = machine['subnet']
      vpcid = machine['vpc_id']
      route = machine['route_table']
      if subnet not in subnets:
        try:
          build_subnet(subnet,vpcid,route)
          subnets.append(subnet)
          BluePrint.objects(subnet=subnet).update(status='Subnet created')
        except Exception as e:
          print("Something went wrong while creating subnet: "+str(e))
          logger(str(e),"warning")

    machines = json.loads(BluePrint.objects.to_json())
    for machine in machines:
      subnet_id = machine['subnet_id']
      ami_id = machine['ami_id']
      machine_type = machine['machine_type']
      if subnet in subnets and vpc in vpcs:
       try:
         create_machine(subnet_id,ami_id,machine_type)
         BluePrint.objects(host=hostname).update(status='Completed build')
       except Exception as e:
         print("Something went wrong while building the machine "+hostname+' '+str(e))
        logger(str(e),"warning")

    con.close()
    return jsonify({'status': 'Success'})
