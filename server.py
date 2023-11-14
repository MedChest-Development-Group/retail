from flask import Flask, request, render_template, url_for, redirect, session, send_from_directory, send_file
from flask_wtf import FlaskForm
from flask_cors import CORS
from hashlib import sha256
from app.models.client_selector import ClientSelector
from werkzeug.utils import secure_filename
import threading
import sqlite3
import hashlib
from datetime import datetime
import time
import os
import signal
import sys    


# NOTE: Section Header are generated using "ANSI Shadow" ascii art font.


#  ██████╗ ██╗      ██████╗ ██████╗  █████╗ ██╗         ███████╗███████╗████████╗██╗   ██╗██████╗ 
# ██╔════╝ ██║     ██╔═══██╗██╔══██╗██╔══██╗██║         ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ██║  ███╗██║     ██║   ██║██████╔╝███████║██║         ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ██║   ██║██║     ██║   ██║██╔══██╗██╔══██║██║         ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝ 
# ╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║███████╗    ███████║███████╗   ██║   ╚██████╔╝██║     
#  ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     

# Configurable Session Length, in Seconds
SESSION_LENGTH = 3600
threads = []







# ██████╗  █████╗ ████████╗ █████╗ ██████╗  █████╗ ███████╗███████╗    ██╗███╗   ██╗██╗████████╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝    ██║████╗  ██║██║╚══██╔══╝
# ██║  ██║███████║   ██║   ███████║██████╔╝███████║███████╗█████╗      ██║██╔██╗ ██║██║   ██║   
# ██║  ██║██╔══██║   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║██╔══╝      ██║██║╚██╗██║██║   ██║   
# ██████╔╝██║  ██║   ██║   ██║  ██║██████╔╝██║  ██║███████║███████╗    ██║██║ ╚████║██║   ██║   
# ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   










##########################################
#      User Database Setup               #
##########################################


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
    password text NOT NULL,
    cityID int,
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
""")
users_connection.commit()
users_cursor.close()

# User DB Accesor Methods
def select_from_users(attribs, condition):
    users_cursor = users_connection.cursor()
    if condition != None:
        query = f'SELECT {attribs} FROM users WHERE {condition}'
    else:
        query = f'SELECT {attribs} FROM users'
    query_results = users_connection.execute(query).fetchall()
    users_cursor.close()
    return query_results

def insert_into_users(first_name, last_name, user_type, username, password, cityID):
    users_cursor = users_connection.cursor()
    query = f'INSERT INTO users(id,first_name,last_name,user_type,username,password, cityID) VALUES (NULL,"{first_name}","{last_name}","{user_type}","{username}","{hashlib.sha256(str.encode(password+"Alittlebitofsaltandpepper.")).hexdigest()}", {cityID})'
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()

def delete_from_users(condition):
    users_cursor = users_connection.cursor()
    query = f'DELETE FROM users WHERE {condition}'
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()








##########################################
#      Token Database Setup              #
##########################################

# Token Database Initialization
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

# Token DB Accesor Methods
def select_from_tokens(attribs, condition):
    tokens_cursor = tokens_connection.cursor()
    if condition != None:
        query = f'SELECT {attribs} FROM tokens WHERE {condition}'
    else:
        query = f'SELECT {attribs} FROM tokens'
    query_results = tokens_connection.execute(query).fetchall()
    tokens_cursor.close()
    return query_results

def insert_into_tokens(token, expire_date):
    tokens_cursor = tokens_connection.cursor()
    query = f'INSERT INTO tokens(token,expire_date) VALUES ("{token}", {expire_date})'
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()

def delete_from_tokens(condition):
    tokens_cursor = tokens_connection.cursor()
    if condition != None:
        query = f'DELETE FROM tokens WHERE {condition}'
    else:
        query = 'DELETE FROM tokens'
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()










##########################################
#      City Database Setup               #
##########################################
cities_connection = sqlite3.connect("cities.db", check_same_thread=False)
cities_cursor = cities_connection.cursor()
cities_cursor.execute("""
CREATE TABLE IF NOT EXISTS cities (
    cityID integer PRIMARY KEY,
    city text NOT NULL,
    state text NOT NULL
)
""")
cities_connection.commit()
cities_cursor.close()


# City DB Accesor Methods
def select_from_cities(attribs, condition):
    cities_cursor = cities_connection.cursor()
    if condition != None:
        query = f'SELECT {attribs} FROM cities WHERE {condition}'
    else:
        query = f'SELECT {attribs} FROM cities'
    query_results = cities_connection.execute(query).fetchall()
    cities_cursor.close()
    return query_results

def insert_into_cities(city, state):
    cities_cursor = cities_connection.cursor()
    query = f'INSERT INTO cities(cityID, city, state) VALUES (NULL, "{city}", "{state}")'
    cities_connection.execute(query)
    cities_connection.commit()
    cities_cursor.close()

def delete_from_cities(condition):
    cities_cursor = cities_connection.cursor()
    if condition != None:
        query = f'DELETE FROM cities WHERE {condition}'
    else:
        query = 'DELETE FROM cities'
    cities_connection.execute(query)
    cities_connection.commit()
    cities_cursor.close()

def initialize_client_selector():
    return sorted([(result[0], ", ".join([name.title() for name in result[1:]])) for result in select_from_cities("*", None)], key= lambda x: x[1])









##########################################
#      Messages Database Setup           #
##########################################
messages_connection = sqlite3.connect("messages.db", check_same_thread=False)
messages_cursor = messages_connection.cursor()
messages_cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    messageID integer PRIMARY KEY,
    content text,
    cityID text,
    timestamp int,
    author text,
    FOREIGN KEY(author) REFERENCES users(username),
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
""")
messages_connection.commit()
messages_cursor.close()


# Message DB Accessor Methods
def select_from_messages(attribs, condition):
    messages_cursor = messages_connection.cursor()
    if condition != None:
        query = f'SELECT {attribs} FROM messages WHERE {condition}'
    else:
        query = f'SELECT {attribs} FROM messages'
    query_results = messages_connection.execute(query).fetchall()
    messages_cursor.close()
    return query_results

def insert_into_messages(content, cityID, timestamp, author):
    messages_cursor = messages_connection.cursor()
    query = f'INSERT INTO messages(messageID, content, cityID, timestamp, author) VALUES (NULL, "{content}", {cityID}, {timestamp}, "{author}")'
    messages_connection.execute(query)
    messages_connection.commit()
    messages_cursor.close()

def delete_from_messages(condition):
    messages_cursor = messages_connection.cursor()
    if condition != None:
        query = f'DELETE FROM messages WHERE {condition}'
    else:
        query = 'DELETE FROM messages'
    messages_connection.execute(query)
    messages_connection.commit()
    messages_cursor.close()



##########################################
#          File Database Setup           #
##########################################
# File database initialization
# The files database can be created
# However schema should be discussed among group
# Especially since there clientIDs will determine who has access
# But no client database is in place
files_connection = sqlite3.connect("files.db", check_same_thread=False)
files_cursor = files_connection.cursor()
files_cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    fileHash text,
    filename text,
    cityID INTEGER,
    PRIMARY KEY(fileHash, cityID),
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
""")
files_connection.commit()
files_cursor.close()

# file DB Accessor Methods
def select_from_files(attribs, condition):
    files_cursor = files_connection.cursor()
    if condition != None:
        query = f'SELECT {attribs} FROM files WHERE {condition}'
    else:
        query = f'SELECT {attribs} FROM files'
    query_results = files_connection.execute(query).fetchall()
    files_cursor.close()
    return query_results

def insert_into_files(fileHash, filename, cityID):
    files_cursor = files_connection.cursor()
    query = f'INSERT INTO files(fileHash, filename, cityID) VALUES ("{fileHash}", "{filename}", {cityID})'
    files_connection.execute(query)
    files_connection.commit()
    files_cursor.close()

def delete_from_files(condition):
    files_cursor = files_connection.cursor()
    if condition != None:
        query = f'DELETE FROM files WHERE {condition}'
    else:
        query = 'DELETE FROM files'
    files_connection.execute(query)
    files_connection.commit()
    files_cursor.close()












# ██████╗ ██╗   ██╗██████╗ ██╗     ██╗ ██████╗    ███████╗ █████╗  ██████╗██╗███╗   ██╗ ██████╗ 
# ██╔══██╗██║   ██║██╔══██╗██║     ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝ 
# ██████╔╝██║   ██║██████╔╝██║     ██║██║         █████╗  ███████║██║     ██║██╔██╗ ██║██║  ███╗
# ██╔═══╝ ██║   ██║██╔══██╗██║     ██║██║         ██╔══╝  ██╔══██║██║     ██║██║╚██╗██║██║   ██║
# ██║     ╚██████╔╝██████╔╝███████╗██║╚██████╗    ██║     ██║  ██║╚██████╗██║██║ ╚████║╚██████╔╝
# ╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝╚═╝  ╚═══╝ ╚═════╝     
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
# This allows you to see HTML/CSS changes when you reload the page when you're running and editing the app locally
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Upload files parameters
UPLOAD_FOLDER_PATH = 'app/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_PATH
# 10 MB file limit
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024



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
    password = request.get_json().get('password')
    username = request.get_json().get('username')

    query_results=select_from_users("user_type,cityID", f'username = "{username}" AND password = "{hashlib.sha256(str.encode(str(password)+"Alittlebitofsaltandpepper.")).hexdigest()}"')
    if(len(query_results) > 0):
        timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        token = hashlib.sha256(str.encode(str(timestamp))).hexdigest()
        session["token"] = token
        insert_into_tokens(token, timestamp+SESSION_LENGTH)
        if(query_results[0][1] != None):
            session["cityID"] = query_results[0][1]
        if(query_results[0][0] == "client"):
            session["type"] = "city"
            return {'window': 'city'}, 200
        else:
            session["type"] = "company"
            return {'window': 'company'}, 200
    else:
        return {'window': 'failed_auth'}, 200
    

@app.route('/upload', methods=["GET"])
def upload():
    form = ClientSelector()
    form.clients.choices = initialize_client_selector()
    return render_template('upload.html', form=form)

@app.route('/uploader', methods=['POST'])
def uploader():
    
    if request.method == 'POST' and token_valid() and "type" in session and session["type"] == "company":
        f = request.files['file']
        try:
            f.save(UPLOAD_FOLDER_PATH+secure_filename(f.filename))
            with open(UPLOAD_FOLDER_PATH+secure_filename(f.filename), mode='rb') as saved:
                insert_into_files(sha256(saved.read()).hexdigest(), secure_filename(f.filename), request.form.get('clients'))
        except sqlite3.IntegrityError:
            print("File already uploaded.")
        except IsADirectoryError:
            print("No file provided.")
    else:
        return redirect("/")
        
        
    return redirect(url_for(".company", client=request.form.get('clients')))

@app.route('/download/<hash>')
def download(hash):
    if token_valid() and "type" in session and session["type"] == "company":
        file = select_from_files("*", f"fileHash = '{hash}'")[0]
        return send_file(UPLOAD_FOLDER_PATH+file[1], 
                     download_name=file[1], as_attachment=True)
    else:
        return redirect("/")
    
@app.route('/deleter/<hash>/<cityID>')
def delete(hash, cityID):
    if token_valid() and "type" in session and session["type"] == "company":
        os.remove(UPLOAD_FOLDER_PATH+select_from_files("filename", f"fileHash = '{hash}' AND cityID = '{cityID}'")[0][0])
        delete_from_files(f"fileHash = '{hash}' AND cityID = '{cityID}'")
        # print("File deleted.")
        return redirect(url_for(".company", client=cityID))
    else:
        return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
    delete_from_tokens(f'token="{session["token"]}"')
    session.clear()
    return redirect("/")

@app.route('/city', methods=["GET"])
def city():
    if token_valid() and "type" in session and session["type"] == "city":
        return render_template('city/home.html')
    else:
        return redirect("/")

@app.route('/company', methods=["GET", "POST"])
def company(client=1):
    form = ClientSelector()
    form.clients.choices = initialize_client_selector()
    if request.method == "POST":
        form.clients.default = request.form.get('clients')
    elif "client" in request.args:
        form.clients.default = request.args["client"]
    else:
        form.clients.default = client

    form.process()
    files = select_from_files("*", f"cityID = {form.clients.default}")

    if token_valid() and "type" in session and session["type"] == "company":
        return render_template('company/home.html', form=form, files=files)
    else:
        return redirect("/")

@app.route('/failed_auth', methods=["GET"])
def failed_auth():
    return render_template('error/failed_auth.html')


def token_valid():
    query_results = select_from_tokens("token", f'token="{session["token"]}"')
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
    """
    Fetchs all users and just displays them on the admin page"""
    user_data = select_from_users("*", None)
    city_data = select_from_cities("*", None)
    users = [{'id': user[0], 'first_name': user[1], 'last_name': user[2], 'user_type': user[3], 'username': user[4], 'cityID': user[6]} for user in user_data]
    cities = [{'cityID': city[0], 'city': city[1], 'state': city[2]} for city in city_data]
    return render_template('admin/dashboard.html', users=users, cities=cities)

@appAdmin.route('/create_user', methods=["GET", "POST"])
def create_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        city = request.form['city'].lower()
        state = request.form['state'].lower()
        query_results = select_from_cities("cityID", f'city="{city}" AND state="{state}"')
        if(len(query_results) == 0):
            print("city does not exist, creating")
            insert_into_cities(city,state)
            query_results = select_from_cities("cityID", f'city="{city}" AND state="{state}"')
        insert_into_users(first_name, last_name, user_type, username, password, query_results[0][0])
        return redirect(url_for("admin_page"))
    return render_template('admin/create_user.html')


# ██╗    ██╗███████╗██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
# ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██║ █╗ ██║█████╗  ██████╔╝    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝   
# ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗  
# ╚███╔███╔╝███████╗██████╔╝    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
#  ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝ 

def run_public_page():
    app.run(debug=False, port=5000)
    
def run_admin_page():
    appAdmin.run(debug=False, port=8123)

def token_watchdog():
    while True:
        # print("Token Cleanup")
        delete_from_tokens(f'expire_date<{(datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()}')
        time.sleep(60)


# https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python#1112350
def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == "__main__":
    delete_from_tokens(None)
    threads.append(threading.Thread(target=run_public_page))
    threads.append(threading.Thread(target=run_admin_page))
    threads.append(threading.Thread(target=token_watchdog))
    for i in threads:
        i.start()
    signal.signal(signal.SIGINT, signal_handler)