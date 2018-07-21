from mongoengine import *
from flask import render_template,Flask,jsonify, flash, request
from ansible.playbook import Playbook
import ast
import json
import os
from pygtail import Pygtail
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'Vishnu123456'

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
    return render_template('index.html', title='Home')


@app.route('/discover')
def discover():
    os.popen('ansible-playbook ./ansible/env_setup.yaml > ./ansible/log.txt')
    return jsonify({'status': 'Success'})


@app.route('/start/cloning', methods=['POST','GET'])
def start_migration():
    os.popen('ansible-playbook ./ansible/start_migration.yaml > ./ansible/migration_log.txt')
    return render_template('discover.html',machines=Post.objects,result=BluePrint.objects)


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
    return render_template('discover.html',machines=Post.objects,result=BluePrint.objects)


@app.route('/start/building', methods=['POST','GET'])
def start_building():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    machines = json.loads(BluePrint.objects.to_json())
    for machine in machines:
      vpc = machine['network']
      subnet = machine['subnet']
      ami_id = machine['ami_id']
      hostname = machine['host']
      vpcs = []
      subnets = [] 
      if vpc not in  vpcs:
        try:
          build_vpc()
          vpcs.append(vpc)
        except Exception as e:
          print("Something went wrong while creating vpc: "+str(e))
      if subnet not in subnets:
        try:
          build_subnet()
          subnets.append(subnet)
        except Exception as e:
          print("Something went wrong while creating subnet: "+str(e))
     if subnet in subnets and vpc in vpcs:
       try:
         createmachine(vpc,subnet,ami_id)
       except Exception as e:
         print("Something went wrong while building the machine "+hostname+' '+str(e)) 

@app.route('/blueprint')
def blueprint():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    return render_template('discover.html',machines=Post.objects)


@app.route('/createblueprint', methods=['POST'])
def create_blueprint():
    cidr = ''
    machine_type = ''
    if request.method == 'POST':  #this block is only entered when the form is submitted
        vpc = request.form.get('vpc')
        machine = request.form['machine']
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
        vpcs[vp].append(j)
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
        print machine
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
        print machine
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
        print machine
    def conv_KB(kb):
      gb = int(kb)/1000000
      return gb
    for machine in machines:
      ram = conv_KB(machine['ram'].split(' ')[0])
      machine['machine_type'] = compu(machine_type,int(machine['cores']),ram)
      #print compu(machine_type,int(machine['cores']),ram)
      post = BluePrint(host=machine['host'], ip=machine['ip'], subnet=machine['subnet'], network=machine['network'],
                 ports=machine['ports'], cores=machine['cores'], cpu_model=machine['cpu_model'], ram=machine['ram'],machine_type=machine['machine_type'],status='Not started')
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
