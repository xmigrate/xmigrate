from __main__ import app
from pkg.common.nodes import *

@app.route('/add/servers', methods=['POST'])
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
  return render_template('index.html', title='Home')
