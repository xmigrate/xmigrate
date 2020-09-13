from __main__ import app
import pexpect
from utils.dbconn import *
from model.discover import *
import ast
from quart import render_template,Flask,jsonify, flash, request
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/')
@app.route('/index')
@jwt_required
def index():
   # pexpect.run('rm ../ansible/log.txt')
    #pexpect.run('touch ../ansible/log.txt')
  #  con = create_db_con()
    #result = Post.objects.exclude('id').to_json()
   # result = ast.literal_eval(result)
    #con.close()
    #return render_template('index.html', title='Home')
    return jsonify({"message":"Good luck"})
