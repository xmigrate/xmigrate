from mongoengine import *
from flask import render_template,Flask,jsonify, flash
from ansible.playbook import Playbook
import ast
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



def ec2_type():
    general = []
    general.append({'name': 't2.nano', 'cores': 1, 'ram': 0.5})
    general.append({'name': 't2.micro', 'cores': 1, 'ram': 1})
    general.append({'name': 't2.small', 'cores': 1, 'ram': 2})
    general.append({'name': 't2.medium', 'cores': 2, 'ram': 4})
    general.append({'name': 't2.large', 'cores': 2, 'ram': 8})
    general.append({'name': 't2.xlarge', 'cores': 4, 'ram': 16})
    general.append({'name': 't2.2xlarge', 'cores': 8, 'ram': 32})
    compute = []
    compute.append({'name': 'c5.large', 'cores': 2, 'ram': 4})
    compute.append({'name': 'c5.xlarge', 'cores': 4, 'ram': 8})
    compute.append({'name': 'c5.2xlarge', 'cores': 8, 'ram': 16})
    compute.append({'name': 'c5.4xlarge', 'cores': 16, 'ram': 32})
    compute.append({'name': 'c5.9xlarge', 'cores': 36, 'ram': 72})
    compute.append({'name': 'c5.18xlarge', 'cores': 72, 'ram': 144})
    compute.append({'name': 'c5d.large', 'cores': 2, 'ram': 4})
    compute.append({'name': 'c5d.xlarge', 'cores': 4, 'ram': 8})
    compute.append({'name': 'c5d.2xlarge', 'cores': 8, 'ram': 16})
    compute.append({'name': 'c5d.4xlarge', 'cores': 16, 'ram': 32})
    compute.append({'name': 'c5d.9xlarge', 'cores': 32, 'ram': 72})
    compute.append({'name': 'c5d.18xlarge', 'cores': 72, 'ram': 144})

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



@app.route('/stream')
def stream():
    line = ''
    line = start_discovery()
    return jsonify({'line':line})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
