from flask import Flask,request,render_template,redirect,url_for,session
from flask_cors import CORS
import threading
import sqlite3
import hashlib
import os


#  ██████╗ ██╗      ██████╗ ██████╗  █████╗ ██╗         ███████╗███████╗████████╗██╗   ██╗██████╗ 
# ██╔════╝ ██║     ██╔═══██╗██╔══██╗██╔══██╗██║         ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ██║  ███╗██║     ██║   ██║██████╔╝███████║██║         ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ██║   ██║██║     ██║   ██║██╔══██╗██╔══██║██║         ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝ 
# ╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║███████╗    ███████║███████╗   ██║   ╚██████╔╝██║     
#  ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     

# User Database Initialization
users_connection = sqlite3.connect("users.db", check_same_thread=False)
users_cursor = users_connection.cursor()
users_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    user_type text NOT NULL,
    username text NOT NULL,
    password text NOT NULL
)
""")
users_connection.commit()
users_cursor.close()











# ██████╗ ██╗   ██╗██████╗ ██╗     ██╗ ██████╗    ███████╗ █████╗  ██████╗██╗███╗   ██╗ ██████╗ 
# ██╔══██╗██║   ██║██╔══██╗██║     ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝ 
# ██████╔╝██║   ██║██████╔╝██║     ██║██║         █████╗  ███████║██║     ██║██╔██╗ ██║██║  ███╗
# ██╔═══╝ ██║   ██║██╔══██╗██║     ██║██║         ██╔══╝  ██╔══██║██║     ██║██║╚██╗██║██║   ██║
# ██║     ╚██████╔╝██████╔╝███████╗██║╚██████╗    ██║     ██║  ██║╚██████╗██║██║ ╚████║╚██████╔╝
# ╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝╚═╝  ╚═══╝ ╚═════╝     


app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
# This allows you to see HTML/CSS changes when you reload the page when you're running and editing the app locally
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Configure app to support user sessions
app.secret_key = os.urandom(32)
CORS(app)

@app.route('/', methods=["GET"])
def base_page():
    return render_template('login.html')


@app.route('/auth', methods=["POST"])
def auth():
    users_cursor = users_connection.cursor()
    password = request.get_json().get('password')
    username = request.get_json().get('username')
    print(password)
    print(username)
    query = f'SELECT user_type FROM users WHERE username = "{username}" AND password = "{hashlib.sha256(str.encode(str(password)+"Alittlebitofsaltandpepper.")).hexdigest()}"'
    query_results=users_cursor.execute(query).fetchall()
    users_cursor.close()
    print(query_results)
    if(query_results):
        session["username"] = username  # set user as logged in
        if(query_results[0][0] == "client"):
            return {'window': 'city'}, 200
        else:
            return {'window': 'company'}, 200
    else:
        return {'window': 'failed_auth'}, 200

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route('/city', methods=["GET"])
def city():
    return render_template('city/home.html')

@app.route('/company', methods=["GET"])
def company():
    return render_template('company/home.html')

@app.route('/failed_auth', methods=["GET"])
def failed_auth():
    return render_template('error/failed_auth.html')







#  █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗
# ██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║
# ███████║██║  ██║██╔████╔██║██║██╔██╗ ██║
# ██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝   


appAdmin = Flask(__name__, template_folder='app/templates', static_folder='app/static')


@appAdmin.route('/', methods=["GET"])
def admin_page():
    return render_template('admin/dashboard.html')

@appAdmin.route('/create_user', methods=["GET"])
def create_user():
    users_cursor = users_connection.cursor()
    query = f'INSERT INTO users(id,first_name,last_name,user_type,username,password) VALUES (NULL,"Test","User","client","tuser123","{hashlib.sha256(str.encode("mypassword"+"Alittlebitofsaltandpepper.")).hexdigest()}")'
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()
    return admin_page()











# ██╗    ██╗███████╗██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
# ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██║ █╗ ██║█████╗  ██████╔╝    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝   
# ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗  
# ╚███╔███╔╝███████╗██████╔╝    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
#  ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝ 

def public_page():
    app.run(debug=False, port=5000)
def admin_page():
    appAdmin.run(debug=False, port=8123)

if __name__ == "__main__":
    threads = []
    threads.append(threading.Thread(target=public_page))
    threads.append(threading.Thread(target=admin_page))

    for i in threads:
        i.start()
    for i in threads:
        i.join()
    