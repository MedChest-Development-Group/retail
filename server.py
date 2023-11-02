from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import threading
import sqlite3
import hashlib
from datetime import datetime
import time
import os
import signal
import sys


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



# User Database Initialization
tokens_connection = sqlite3.connect("tokens.db", check_same_thread=False)
tokens_cursor = tokens_connection.cursor()
tokens_cursor.execute("""
CREATE TABLE IF NOT EXISTS tokens (
    token text PRIMARY KEY,
    expire_date int
)
""")
tokens_connection.commit()
tokens_cursor.close()

# Configurable Session Length, in Seconds
SESSION_LENGTH = 60
threads = []




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

@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype = 'image/vnd.microsoft.icon')

@app.route('/auth', methods=["POST"])
def auth():
    users_cursor = users_connection.cursor()
    password = request.get_json().get('password')
    username = request.get_json().get('username')
    # print(password)
    # print(username)
    query = f'SELECT user_type FROM users WHERE username = "{username}" AND password = "{hashlib.sha256(str.encode(str(password)+"Alittlebitofsaltandpepper.")).hexdigest()}"'
    query_results=users_cursor.execute(query).fetchall()
    users_cursor.close()
    # print(query_results)
    if(len(query_results) > 0):
        timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        token = hashlib.sha256(str.encode(str(timestamp))).hexdigest()
        session["token"] = token

        tokens_cursor = tokens_connection.cursor()
        query = f'INSERT INTO tokens(token,expire_date) VALUES ("{token}", {timestamp+SESSION_LENGTH})'
        tokens_connection.execute(query)
        tokens_connection.commit()
        tokens_cursor.close()

        if(query_results[0][0] == "client"):
            session["type"] = "city"
            return {'window': 'city'}, 200
        else:
            session["type"] = "company"
            return {'window': 'company'}, 200
    else:
        return {'window': 'failed_auth'}, 200

@app.route("/logout", methods=["GET"])
def logout():
    tokens_cursor = tokens_connection.cursor()
    query = f'DELETE FROM tokens WHERE token="{session["token"]}"'
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()
    session.clear()
    return redirect("/")

@app.route('/city', methods=["GET"])
def city():
    if token_valid() and ("type" in session) and session["type"] == "city":
        return render_template('city/home.html')
    else:
        return redirect("/")

@app.route('/company', methods=["GET"])
def company():
    if token_valid() and "type" in session and session["type"] == "company":
        return render_template('company/home.html')
    else:
        return redirect("/")

@app.route('/failed_auth', methods=["GET"])
def failed_auth():
    return render_template('error/failed_auth.html')


def token_valid():
    tokens_cursor = tokens_connection.cursor()
    query = f'SELECT token FROM tokens WHERE token="{session["token"]}"'
    query_results = tokens_connection.execute(query).fetchall()
    print("token_valid result: "+str(query_results))
    tokens_cursor.close()
    return True if len(query_results) > 0 else False




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

def token_watchdog():
    while True:
        print("Token Cleanup")
        tokens_cursor = tokens_connection.cursor()
        query = f'DELETE FROM tokens WHERE expire_date<{(datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()}'
        tokens_connection.execute(query)
        tokens_connection.commit()
        tokens_cursor.close()
        time.sleep(60)


# https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python#1112350
def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == "__main__":
    tokens_cursor = tokens_connection.cursor()
    query = f'DELETE FROM tokens'
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()
    threads.append(threading.Thread(target=public_page))
    threads.append(threading.Thread(target=admin_page))
    threads.append(threading.Thread(target=token_watchdog))
    for i in threads:
        i.start()
    signal.signal(signal.SIGINT, signal_handler)