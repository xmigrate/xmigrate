from __main__ import app
from pkg.common.nodes import *
from quart import request,render_template
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/add/servers', methods=['POST'])
@jwt_required
def add_servers():
  if request.method == 'POST':
    ips = request.form['ips']
    user = request.form['user']
    password = request.form['password']
    nodes = ips.split(',')
    try:
      add_nodes(nodes,user,password)
    except Exception as e:
      print(e)
      logger(str(e),"warning")
  return render_template('index.html', title='Home')
