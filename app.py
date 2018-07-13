from mongoengine import *
from flask import render_template,Flask,jsonify, flash, request
from ansible.playbook import Playbook
import ast
import json
import os
from pygtail import Pygtail



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

def compu(name,core,ram):
    if name=='GeneralPurpose':
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
    elif name=='ComputeOptimizes':
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


@app.route('/blueprint')
def blueprint():
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    return render_template('discover.html',machines=Post.objects)


@app.route('/createblueprint', methods=['POST'])
def create_blueprint():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        vpc = request.form.get('vpc')
        machine = request.form['machine']
        if vpc == 1:
          cidr = '10.0.0.0.0'
        elif vpc == 2:
          cidr = '172.16.0.0'
        elif vpc == 3:
          cidr = '192.168.0.0'
        if machine == 1:
          machine_type = 'general'
        else:
          machine_type = 'compute'
    con = connect(host="mongodb://migrationuser:mygrationtool@localhost:27017/migration?authSource=admin")
    machines = json.loads(Post.objects.to_json())
    networks = []
    for machine in machines:
      networks.append(machine['network'])
    network_count = len(list(set(networks)))
    networks = list(set(networks))
    return render_template('discover.html',machines=Post.objects)


@app.route('/stream')
def stream():
    line = ''
    line = start_discovery()
    return jsonify({'line':line})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
