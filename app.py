from mongoengine import *
from flask import render_template,Flask,jsonify, flash, request
from ansible.playbook import Playbook
import ast
import json
import os
from pygtail import Pygtail
from collections import defaultdict
import boto3
from create_ami import start_ami_creation
app = Flask(__name__)
app.secret_key = 'Vishnu123456'

bucket_name = 'migrationdata2'

def start_discovery():
    l = ''
    f = open('./ansible/log.txt','r')
    l = f.read()
    return l


class Post(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    disk = StringField(required=True, max_length=50)


class BluePrint(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    machine_type = StringField(required=True, max_length=150)
    status = StringField(required=False, max_length=100)
    ami_id = StringField(required=False, max_length=100)
    vpc_id = StringField(required=False, max_length=100)
    subnet_id = StringField(required=False, max_length=100)
    public_route = BooleanField(required=False)
    ig_id = StringField(required=False, max_length=100)
    route_table = StringField(required=False, max_length=100)
    instance_id = StringField(required=False, max_length=100)


def build_vpc(cidr,public_route):
  ec2 = boto3.resource('ec2')
  vpc = ec2.create_vpc(CidrBlock=cidr)
  #vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
  vpc.wait_until_available()
  con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
  BluePrint.objects(network=cidr).update(vpc_id = vpc.id)
  if public_route:
    ig = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=ig.id)
    BluePrint.objects(network=cidr).update(ig_id=ig.id)
    route_table = vpc.create_route_table()
    route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=ig.id)
    BluePrint.objects(network=cidr).update(route_table=route_table.id)
  con.close()

def build_subnet(cidr,vpcid,route):
    ec2 = boto3.resource('ec2')
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    route_table = ec2.RouteTable(route)
    subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpcid)
    BluePrint.objects(subnet=cidr).update(subnet_id=subnet.id)
    route_table.associate_with_subnet(SubnetId=subnet.id)
    con.close()

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

def compu(name,core,ram):
    if name=='general':
        if core==1 and ram==0.5:
            return('t2.nano')
        elif core==1 and ram==1:
            return('t2.micro')
        elif core==1 and ram==2:
            return('t2.small')
        elif core==2 and ram==4:
            return('t2.medium')
        elif core==2 and ram==8:
            return('t2.large')
        elif core==4 and ram==16:
            return('t2.namelarge')
        elif core==8 and ram==32:
            return('t2.2namelarge')
        elif core==2 and ram==38:
            return('m5.large')
        elif core==4 and ram==16:
            return('m5.namelarge')
        elif core==8 and ram==32:
            return('m5.2namelarge') 
        elif core==16 and ram==64:
            return('m5.4namelarge')     
        elif core==48 and ram==192:
            return('m5.12namelarge')
        elif core==96 and ram==384:
            return('m5.24namelarge')
        elif core==2 and ram==8:
            return('m5d.large')
        elif core==4 and ram==16:
            return('m5d.namelarge')
        elif core==8 and ram==32:
            return('m5d.2namelarge')
        elif core==8 and ram==32:
            return('m5d.2namelarge')
        elif core==16 and ram==64:
            return('m5d.4namelarge')   
        elif core==48 and ram==192:
            return('m5d.12namelarge')
        elif core==96 and ram==384:
            return('m5d.24namelarge')
        else:
            return("No machines found")            
    elif name=='compute':
        if core==2 and ram==4:
            return('c5.large')
        elif core==4 and ram==8:
            return('c5.namelarge')
        elif core==8 and ram==16:
            return('c5.2namelarge')
        elif core==16 and ram==32:
            return('c5.4namelarge')  
        elif core==72 and ram==144:
            return('c5.18namelarge')
        elif core==2 and ram==4:
            return('c5d.large')
        elif core==4 and ram==8:
            return('c5d.namelarge')
        elif core==8 and ram==32:
            return('c5d.2namelarge')
        elif core==16 and ram==64:
            return('c5d.4namelarge')
        elif core==32 and ram==72:
            return('c5d.9namelarge')
        elif core==72 and ram==144:
            return('c5d.18namelarge')
        elif core==2 and ram==3.75:
            return('c4.large')
        elif core==4 and ram==7.5:
            return('c4.namelarge')
        elif core==8 and ram==15:
            return('c4.2namelarge')
        elif core==16 and ram==30:
            return('c4.4namelarge')
        elif core==36 and ram==60:
            return('c4.8namelarge')
        else:
            return("No machines found")



@app.route('/')
@app.route('/index')
def index():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    result = Post.objects.exclude('id').to_json()
    result = ast.literal_eval(result)
    con.close()
    return render_template('index.html', title='Home')


@app.route('/discover')
def discover():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    Post.objects.delete()
    con.close()
    os.popen('ansible-playbook ./ansible/env_setup.yaml > ./ansible/log.txt')
    return jsonify({'status': 'Success'})


@app.route('/start/cloning', methods=['POST','GET'])
def start_migration():
    os.popen('ansible-playbook ./ansible/start_migration.yaml > ./ansible/migration_log.txt')
    return jsonify({'status': 'Success'})

@app.route('/start/conversion', methods=['POST','GET'])
def start_conversion():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    machines = json.loads(Post.objects.to_json())
    for machine in machines:
      img_name = machine['host']+'.img'
      try:
        start_ami_creation(bucket_name,img_name)
      except Exception as e:
        print("Boss you have to see this error: "+str(e))
    return jsonify({'status': 'Success'})


@app.route('/start/building', methods=['POST','GET'])
def start_building():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
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
    machines = json.loads(BluePrint.objects.to_json())
    for machine in machines:
      subnet_id = machine['subnet_id']
      ami_id = machine['ami_id']
      machine_type = machine['machine_type']
      if subnet in subnets and vpc in vpcs:
       try:
         createmachine(subnet_id,ami_id,machine_type)
         BluePrint.objects(host=hostname).update(status='Completed build')
       except Exception as e:
         print("Something went wrong while building the machine "+hostname+' '+str(e)) 
    return jsonify({'status': 'Success'})


@app.route('/migration/status')
def migration_status():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    machines = json.loads(BluePrint.objects.to_json())
    return jsonify(machines)

@app.route('/blueprint')
def blueprint():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    return render_template('discover.html',machines=Post.objects)


@app.route('/createblueprint', methods=['POST'])
def create_blueprint():
    cidr = ''
    machine_type = ''
    pubr = ''
    if request.method == 'POST':  #this block is only entered when the form is submitted
        vpc = request.form.get('vpc')
        machine = request.form['machine']
        pub = request.form['public']
        if vpc == '1':
          cidr = '10.0.0.0'
        elif vpc == '2':
          cidr = '172.16.0.0'
        elif vpc == '3':
          cidr = '192.168.0.0'
        if machine == '1':
          machine_type = 'general'
        else:
          machine_type = 'compute'
        if pub == '1':
           pubr = True
        else:
           pubr = False
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    try:
      BluePrint.objects.delete()
    except Exception as e:
      print "See the error:"+ str(e)      
    machines = json.loads(Post.objects.to_json())
    networks = []
    for machine in machines:
      networks.append(machine['network'])
    network_count = len(list(set(networks)))
    networks = list(set(networks))
    vpc_cidr = defaultdict(list)
    subnet_machines = defaultdict(list)
    vpcs = defaultdict(list)
    for i in machines:
      vpc_cidr[i['network']].append(i['subnet'])
    for i in vpc_cidr.keys():
      subnet_prefixes = []
      subnet_prefix = 0
      for j in vpc_cidr[i]:
        subnet_prefixes.append(int(j.split('/')[-1]))
        subnet_prefix = min(subnet_prefixes)
        vp = i+'/'+str(subnet_prefix-2)
        if '/' not in i:
          Post.objects(network=i).update(network=vp)
    print vpcs
    machines = json.loads(Post.objects.to_json())
    if cidr == '10.0.0.0':
      for machine in machines:
        if machine['network'].split('.')[0] == '10':
          continue
        machine['ip'] = machine['ip'].split('.')
        machine['ip'][0] = '10'
        machine['ip'] = '.'.join(machine['ip'])
        machine['network'] = machine['network'].split('.')
        machine['network'][0] = '10'
        machine['network'] = '.'.join(machine['network'])
        machine['subnet'] = machine['subnet'].split('.')
        machine['subnet'][0] = '10'
        machine['subnet'] = '.'.join(machine['subnet'])
       # print machine
    elif cidr == '172.16.0.0':
      for machine in machines:
        if machine['network'].split('.')[0] == '172':
          continue
        machine['ip'] = machine['ip'].split('.')
        machine['ip'][0] = '172'
        machine['ip'][1] = '16'
        machine['ip'] = '.'.join(machine['ip'])
        machine['network'] = machine['network'].split('.')
        machine['network'][0] = '172'
        machine['network'][1] = '16'
        machine['network'] = '.'.join(machine['network'])
        machine['subnet'] = machine['subnet'].split('.')
        machine['subnet'][0] = '172'
        machine['subnet'][1] = '16'
        machine['subnet'] = '.'.join(machine['subnet'])
        #print machine
    elif cidr == '192.168.0.0':
      for machine in machines:
        if machine['network'].split('.')[0] == '192':
          continue
        machine['ip'] = machine['ip'].split('.')
        machine['ip'][0] = '192'
        machine['ip'][1] = '168'
        machine['ip'] = '.'.join(machine['ip'])
        machine['network'] = machine['network'].split('.')
        machine['network'][0] = '192'
        machine['network'][1] = '168'
        machine['network'] = '.'.join(machine['network'])
        machine['subnet'] = machine['subnet'].split('.')
        machine['subnet'][0] = '192'
        machine['subnet'][1] = '168'
        machine['subnet'] = '.'.join(machine['subnet'])
        #print machine
    def conv_KB(kb):
      gb = int(kb)/1000000
      return gb
    for machine in machines:
      ram = conv_KB(machine['ram'].split(' ')[0])
      machine['machine_type'] = compu(machine_type,int(machine['cores']),ram)
      #print compu(machine_type,int(machine['cores']),ram)
      post = BluePrint(host=machine['host'], ip=machine['ip'], subnet=machine['subnet'], network=machine['network'],
                 ports=machine['ports'], cores=machine['cores'], public_route=pubr, cpu_model=machine['cpu_model'], ram=machine['ram'],machine_type=machine['machine_type'],status='Not started')
      try:
        post.save()
      except Exception as e:
        print("Boss you have to see this!!")
        print(e)
      finally:
        con.close()
    return render_template('discover.html',machines=Post.objects,result=BluePrint.objects)



@app.route('/stream')
def stream():
    line = ''
    line = start_discovery()
    return jsonify({'line':line})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
