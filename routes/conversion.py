from __main__ import app
from utils.dbconn import *
from model.discover import *
from pkg.aws.create_ami import *

@app.route('/start/conversion', methods=['POST','GET'])
def start_conversion():
    con = create_db_con()
    machines = json.loads(Post.objects.to_json())
    for machine in machines:
      img_name = machine['host']+'.img'
      try:
        start_ami_creation(bucket_name,img_name)
      except Exception as e:
        print("Boss you have to see this error: "+str(e))
    con.close()
    return jsonify({'status': 'Success'})
