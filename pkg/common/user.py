from utils.dbconn import *
from model.user import *

def add_user(username, password):
    con = create_db_con()
    post = User(username=username, password=password)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()

def check_user(username, password):
    con = create_db_con()
    try:
        if User.objects(username=username, password=password).count() == 1:
            return True
        else:
            return False
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()