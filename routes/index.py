from __main__ import app
import pexpect
from utils.dbconn import *
from model.discover import *
import ast
from flask import render_template,Flask,jsonify, flash, request

@app.route('/')
@app.route('/index')
def index():
   # pexpect.run('rm ../ansible/log.txt')
    #pexpect.run('touch ../ansible/log.txt')
  #  con = create_db_con()
    #result = Post.objects.exclude('id').to_json()
   # result = ast.literal_eval(result)
    #con.close()
    #return render_template('index.html', title='Home')
    return jsonify({"message":"fuck you!!"})
