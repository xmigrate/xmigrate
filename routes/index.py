from app import app
from quart import render_template,jsonify, flash, request
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/')
@app.route('/index')
@jwt_required
def index():
   # pexpect.run('rm ../ansible/log.txt')
    #pexpect.run('touch ../ansible/log.txt')
  #  con = create_db_con()
    #result = Post.objects.exclude('id').allow_filtering()
   # result = ast.literal_eval(result)
    #con.shutdown()
    #return render_template('index.html', title='Home')
    return jsonify({"message":"Good luck"})
