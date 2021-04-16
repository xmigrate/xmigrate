from __main__ import app
from utils.dbconn import *
from model.discover import *
from flask import render_template,Flask,jsonify, flash, request

@app.route('/blueprint')
def blueprint():
    con = create_db_con()
    return render_template('discover.html',machines=Discover.objects)


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
    con = create_db_con()
    try:
      BluePrint.objects.delete()
    except Exception as e:
      print("See the error:"+ str(e))
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
    print(vpcs)
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
      post = BluePrint(host=machine['host'], ip=machine['ip'], subnet=machine['subnet'], network=machine['network'],
                 ports=machine['ports'], cores=machine['cores'], public_route=pubr, cpu_model=machine['cpu_model'], ram=machine['ram'],machine_type=machine['machine_type'],status='Not started')
      try:
        post.save()
      except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
      finally:
        con.close()
    return render_template('discover.html',machines=Post.objects,result=BluePrint.objects)
