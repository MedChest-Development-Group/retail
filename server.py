from flask import (
    Flask,
    request,
    render_template,
    url_for,
    redirect,
    session,
    send_from_directory,
    send_file,
    make_response,
)
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
users_cursor.execute(
    """
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
"""
)
users_connection.commit()
users_cursor.close()







"""
Retrieve data from the 'users' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str, optional): SQL condition to filter the results. Default is None.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_users(attribs, condition):
    users_cursor = users_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM users WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM users"
    query_results = users_connection.execute(query).fetchall()
    users_cursor.close()
    return query_results

"""
Insert a new user into the 'users' table.

Parameters:
- first_name (str): First name of the user.
- last_name (str): Last name of the user.
- user_type (str): Type of the user (e.g., 'admin', 'regular').
- username (str): Unique username for the user.
- password (str): Password for the user (hashed using SHA-256 with salt).
- cityID (int): ID of the city to which the user belongs.
"""
def insert_into_users(first_name, last_name, user_type, username, password, cityID):
    users_cursor = users_connection.cursor()
    query = f'INSERT INTO users(id,first_name,last_name,user_type,username,password, cityID) VALUES (NULL,"{first_name}","{last_name}","{user_type}","{username}","{hashlib.sha256(str.encode(password+"Alittlebitofsaltandpepper.")).hexdigest()}", {cityID})'
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()

"""
Delete user(s) from the 'users' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the users to be deleted.
"""
def delete_from_users(condition):
    users_cursor = users_connection.cursor()
    query = f"DELETE FROM users WHERE {condition}"
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()


##########################################
#      Token Database Setup              #
##########################################

# Token Database Initialization
tokens_connection = sqlite3.connect("tokens.db", check_same_thread=False)
tokens_cursor = tokens_connection.cursor()
tokens_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS tokens (
    token text PRIMARY KEY,
    expire_date int
)
"""
)
tokens_connection.commit()
tokens_cursor.close()

"""
Retrieve data from the 'tokens' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str): SQL condition to filter the results.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_tokens(attribs, condition):
    tokens_cursor = tokens_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM tokens WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM tokens"
    query_results = tokens_connection.execute(query).fetchall()
    tokens_cursor.close()
    return query_results


"""
Insert a new token into the 'tokens' table.

Parameters:
- token (str): The token string.
- expire_date (int): The expiration date of the token.
"""
def insert_into_tokens(token, expire_date):
    tokens_cursor = tokens_connection.cursor()
    query = f'INSERT INTO tokens(token,expire_date) VALUES ("{token}", {expire_date})'
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()

"""
Delete token(s) from the 'tokens' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the tokens to be deleted.
"""
def delete_from_tokens(condition):
    tokens_cursor = tokens_connection.cursor()
    if condition != None:
        query = f"DELETE FROM tokens WHERE {condition}"
    else:
        query = "DELETE FROM tokens"
    tokens_connection.execute(query)
    tokens_connection.commit()
    tokens_cursor.close()

##########################################
#      City Database Setup               #
##########################################
cities_connection = sqlite3.connect("cities.db", check_same_thread=False)
cities_cursor = cities_connection.cursor()
cities_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS cities (
    cityID integer PRIMARY KEY,
    city text NOT NULL,
    state text NOT NULL
)
"""
)
cities_connection.commit()
cities_cursor.close()

"""
Retrieve data from the 'cities' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str): SQL condition to filter the results.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_cities(attribs, condition):
    cities_cursor = cities_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM cities WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM cities"
    query_results = cities_connection.execute(query).fetchall()
    cities_cursor.close()
    return query_results

"""
Insert a new city into the 'cities' table.

Parameters:
- city (str): The name of the city.
- state (str): The state to which the city belongs.
"""
def insert_into_cities(city, state):
    cities_cursor = cities_connection.cursor()
    query = (
        f'INSERT INTO cities(cityID, city, state) VALUES (NULL, "{city}", "{state}")'
    )
    cities_connection.execute(query)
    cities_connection.commit()
    cities_cursor.close()

"""
Delete city(s) from the 'cities' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the cities to be deleted.
"""
def delete_from_cities(condition):
    cities_cursor = cities_connection.cursor()
    if condition != None:
        query = f"DELETE FROM cities WHERE {condition}"
    else:
        query = "DELETE FROM cities"
    cities_connection.execute(query)
    cities_connection.commit()
    cities_cursor.close()

"""
Initialize and return a sorted list of tuples for use in selecting cities.

Returns:
- list: A list of tuples containing city information.
"""
def initialize_client_selector():
    return sorted(
        [
            (result[0], ", ".join([name.title() for name in result[1:]]))
            for result in select_from_cities("*", None)
        ],
        key=lambda x: x[1],
    )



##########################################
#      Messages Database Setup           #
##########################################
messages_connection = sqlite3.connect("messages.db", check_same_thread=False)
messages_cursor = messages_connection.cursor()
messages_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS messages (
    messageID integer PRIMARY KEY,
    relativeID integer,
    content text,
    cityID text,
    timestamp int,
    author text,
    edited int,
    FOREIGN KEY(author) REFERENCES users(username),
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
"""
)
messages_connection.commit()
messages_cursor.close()

"""
Retrieve data from the 'messages' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str): SQL condition to filter the results.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_messages(attribs, condition):
    messages_cursor = messages_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM messages WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM messages"
    query_results = messages_connection.execute(query).fetchall()
    messages_cursor.close()
    return query_results

"""
Insert a new message into the 'messages' table.

Parameters:
- messageID (int): ID of the message.
- content (str): The content of the message.
- cityID (int): ID of the city associated with the message.
- timestamp (int): Timestamp of when the message was created.
- author (str): Username of the message author.
"""
def insert_into_messages(messageID, content, cityID, timestamp, author):
    messages_cursor = messages_connection.cursor()
    query = f'INSERT INTO messages(messageID, relativeID, content, cityID, timestamp, author) VALUES (NULL, {messageID}, "{content}", {cityID}, {timestamp}, "{author}")'
    messages_connection.execute(query)
    messages_connection.commit()
    messages_cursor.close()











"""
Delete message(s) from the 'messages' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the messages to be deleted.
"""
def delete_from_messages(condition):
    messages_cursor = messages_connection.cursor()
    if condition != None:
        query = f"DELETE FROM messages WHERE {condition}"
    else:
        query = "DELETE FROM messages"
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
files_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS files (
    fileHash text,
    filename text,
    cityID INTEGER,
    marketingMaterial bool,
    PRIMARY KEY(fileHash, cityID),
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
"""
)
files_connection.commit()
files_cursor.close()













"""
Retrieve data from the 'files' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str): SQL condition to filter the results.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_files(attribs, condition):
    files_cursor = files_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM files WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM files"
    query_results = files_connection.execute(query).fetchall()
    files_cursor.close()
    return query_results










"""
Insert a new file into the 'files' table.

Parameters:
- fileHash (str): The hash of the file.
- filename (str): The name of the file.
- cityID (int): ID of the city associated with the file.
"""
def insert_into_files(fileHash, filename, cityID):
    files_cursor = files_connection.cursor()
    query = f'INSERT INTO files(fileHash, filename, cityID, marketingMaterial) VALUES ("{fileHash}", "{filename}", {cityID}, false)'
    files_connection.execute(query)
    files_connection.commit()
    files_cursor.close()










"""
Update file records in the 'files' table based on specified updates and conditions.

Parameters:
- updates (str): Comma-separated string of attribute updates.
- conditions (str): SQL condition to filter the files to be updated.
"""
def update_files(updates, conditions):
    files_cursor = files_connection.cursor()
    query = f"UPDATE files SET {updates} WHERE {conditions}"
    files_connection.execute(query)
    files_connection.commit()
    files_cursor.close()











"""
Delete file(s) from the 'files' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the files to be deleted.
"""
def delete_from_files(condition):
    files_cursor = files_connection.cursor()
    if condition != None:
        query = f"DELETE FROM files WHERE {condition}"
    else:
        query = "DELETE FROM files"
    files_connection.execute(query)
    files_connection.commit()
    files_cursor.close()


##########################################
#          Cards Database Setup           #
##########################################
cards_connection = sqlite3.connect("cards.db", check_same_thread=False)
cards_cursor = cards_connection.cursor()
cards_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS cards (
    cardID int PRIMARY KEY,
    relativeID integer,
    content text,
    columnID text,
    cityID int,
    FOREIGN KEY(cityID) REFERENCES cities(cityID)
)
"""
)
cards_connection.commit()
cards_cursor.close()










"""
Retrieve data from the 'cards' table based on specified attributes and condition.

Parameters:
- attribs (str): Comma-separated string of attribute names to be retrieved.
- condition (str): SQL condition to filter the results.

Returns:
- list: List of tuples representing the query results.
"""
def select_from_cards(attribs, condition):
    cards_cursor = cards_connection.cursor()
    if condition != None:
        query = f"SELECT {attribs} FROM cards WHERE {condition}"
    else:
        query = f"SELECT {attribs} FROM cards"
    query_results = cards_connection.execute(query).fetchall()
    cards_cursor.close()
    return query_results









"""
Insert a new card into the 'cards' table.

Parameters:
- cardID (int): ID of the card.
- content (str): The content of the card.
- columnID (str): ID of the column to which the card belongs.
- cityID (int): ID of the city associated with the card.
"""
def insert_into_cards(cardID, content, columnID, cityID):
    cards_cursor = cards_connection.cursor()
    query = f'INSERT INTO cards(cardID, relativeID, content, columnID, cityID) VALUES (NULL, {cardID}, "{content}", "{columnID}", {cityID})'
    cards_connection.execute(query)
    cards_connection.commit()
    cards_cursor.close()









"""
Update card records in the 'cards' table based on specified updates and conditions.

Parameters:
- updates (str): Comma-separated string of attribute updates.
- condition (str): SQL condition to filter the cards to be updated.
"""
def update_in_cards(updates, condition):
    cards_cursor = cards_connection.cursor()
    query = f"UPDATE cards SET {updates} WHERE {condition}"
    cards_connection.execute(query)
    cards_connection.commit()
    cards_cursor.close()









"""
Delete card(s) from the 'cards' table based on the specified condition.

Parameters:
- condition (str): SQL condition to filter the cards to be deleted.
"""
def delete_from_cards(condition):
    cards_cursor = cards_connection.cursor()
    if condition != None:
        query = f"DELETE FROM cards WHERE {condition}"
    else:
        query = "DELETE FROM cards"
    cards_connection.execute(query)
    cards_connection.commit()
    cards_cursor.close()










# ██████╗ ██╗   ██╗██████╗ ██╗     ██╗ ██████╗    ███████╗ █████╗  ██████╗██╗███╗   ██╗ ██████╗
# ██╔══██╗██║   ██║██╔══██╗██║     ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝
# ██████╔╝██║   ██║██████╔╝██║     ██║██║         █████╗  ███████║██║     ██║██╔██╗ ██║██║  ███╗
# ██╔═══╝ ██║   ██║██╔══██╗██║     ██║██║         ██╔══╝  ██╔══██║██║     ██║██║╚██╗██║██║   ██║
# ██║     ╚██████╔╝██████╔╝███████╗██║╚██████╗    ██║     ██║  ██║╚██████╗██║██║ ╚████║╚██████╔╝
# ╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝╚═╝  ╚═══╝ ╚═════╝
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")



# This allows you to see HTML/CSS changes when you reload the page when you're running and editing the app locally
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Upload files parameters
UPLOAD_FOLDER_PATH = "app/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER_PATH


# 10 MB file limit
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024


# Configure app to support user sessions
app.secret_key = os.urandom(32)
CORS(app)




"""
Serve the base page of the application.

Endpoint: /
Method: GET

Returns:
- Rendered HTML template "login.html", HTTP status code 200
"""
@app.route("/", methods=["GET"])
def base_page():
    return render_template("login.html")







"""
Serve the favicon.ico file for the application.

Endpoint: /favicon.ico
Method: GET

Returns:
- Favicon.ico file from the 'static' directory, HTTP status code 200
"""
@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )








"""
Authenticate a user by validating the provided username and password.

Endpoint: /auth
Method: POST

JSON Request Payload:
{
    "username": "user_username",
    "password": "user_password"
}

Returns:
- If authentication is successful:
    - For city users: {"window": "city"}, HTTP status code 200
    - For company users: {"window": "company"}, HTTP status code 200
- If authentication fails: {"window": "failed_auth"}, HTTP status code 200
"""
@app.route("/auth", methods=["POST"])
def auth():
    password = request.get_json().get("password")
    username = request.get_json().get("username")


    query_results=select_from_users("user_type,cityID,first_name,last_name", f'username = "{username}" AND password = "{hashlib.sha256(str.encode(str(password)+"Alittlebitofsaltandpepper.")).hexdigest()}"')
    if(len(query_results) > 0):
        timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        token = hashlib.sha256(str.encode(str(timestamp))).hexdigest()
        session["token"] = token
        insert_into_tokens(token, timestamp+SESSION_LENGTH)
        session["first_name"] = query_results[0][2]
        session["last_name"] = query_results[0][3]
        if(query_results[0][1] != None):

            session["cityID"] = query_results[0][1]
        if query_results[0][0] == "city":
            session["type"] = "city"
            return {"window": "city"}, 200
        else:
            session["type"] = "company"
            return {"window": "company"}, 200
    else:
        return {"window": "failed_auth"}, 200










"""
Serve the upload page of the application.

Endpoint: /upload
Method: GET

Returns:
- Rendered HTML template "upload.html" with a populated client selector form, HTTP status code 200
"""
@app.route("/upload", methods=["GET"])
def upload():
    form = ClientSelector()
    form.clients.choices = initialize_client_selector()
    return render_template("upload.html", form=form)









"""
Handle file uploads from company users.

Endpoint: /uploader
Method: POST

Requires:
- POST request method
- Valid session token
- User is authenticated as a company

Form Data:
- "file": File to be uploaded
- "clients": Selected client for the uploaded file

Returns:
- If upload successful: Redirect to the company page for the selected client
- If upload fails or unauthorized: Redirect to the login page
"""
@app.route("/uploader", methods=["POST"])
def uploader():
    if (
        request.method == "POST"
        and token_valid()
        and "type" in session
        and session["type"] == "company"
    ):
        f = request.files["file"]
        try:
            if not os.path.exists(UPLOAD_FOLDER_PATH):
                os.makedirs(UPLOAD_FOLDER_PATH)
            f.save(UPLOAD_FOLDER_PATH+secure_filename(f.filename))
            with open(UPLOAD_FOLDER_PATH+secure_filename(f.filename), mode='rb') as saved:
                insert_into_files(sha256(saved.read()).hexdigest(), secure_filename(f.filename), request.form.get('clients'))
        except sqlite3.IntegrityError:
            print("File already uploaded.")
        except IsADirectoryError:
            print("No file provided.")
    else:
        return redirect("/")

    return redirect(url_for(".company", client=request.form.get("clients")))












"""
Handle file downloads for company users.

Endpoint: /download/<hash>
Method: GET

Requires:
- Valid session token
- User is authenticated as a company

Parameters:
- hash (str): Hash value of the file to be downloaded

Returns:
- If download successful: File download response
- If download fails or unauthorized: Redirect to the login page
"""
@app.route("/download/<hash>")
def download(hash):
    if token_valid() and "type" in session and session["type"] == "company":
        file = select_from_files("*", f"fileHash = '{hash}'")[0]
        return send_file(
            UPLOAD_FOLDER_PATH + file[1], download_name=file[1], as_attachment=True
        )
    else:
        return redirect("/")










"""
Update the marketing material status for a file in a specific city.

Endpoint: /marketingupdate/<hash>/<cityID>/<status>
Method: GET

Requires:
- Valid session token
- User is authenticated as a company

Parameters:
- hash (str): Hash value of the file
- cityID (str): ID of the city associated with the file
- status (str): Updated marketing material status (0 or 1)

Returns:
- If update successful: Redirect to the company page for the specified city
- If update fails or unauthorized: Redirect to the login page
"""
@app.route("/marketingupdate/<hash>/<cityID>/<status>")
def marketingUpdate(hash, cityID, status):
    if token_valid() and "type" in session and session["type"] == "company":
        update_files(f"marketingMaterial = '{1 if int(status) == 0 else 0}'", f"fileHash = '{hash}' AND cityID = '{cityID}'")
        return redirect(url_for(".company", client=cityID))
    else:
        return redirect("/")









"""
Delete a file record associated with a specific hash and city.

Endpoint: /deleter/<hash>/<cityID>
Method: GET

Requires:
- Valid session token
- User is authenticated as a company

Parameters:
- hash (str): Hash value of the file
- cityID (str): ID of the city associated with the file

Returns:
- If deletion successful: Redirect to the company page for the specified city
- If deletion fails or unauthorized: Redirect to the login page
"""
@app.route("/deleter/<hash>/<cityID>")
def delete(hash, cityID):
    if token_valid() and "type" in session and session["type"] == "company":
        if (len(select_from_files("*",f"fileHash = '{hash}'")) <= 1):
            os.remove(
                UPLOAD_FOLDER_PATH
                + select_from_files(
                    "filename", f"fileHash = '{hash}' AND cityID = '{cityID}'"
                )[0][0]
            )
        delete_from_files(f"fileHash = '{hash}' AND cityID = '{cityID}'")
        # print("File deleted.")
        return redirect(url_for(".company", client=cityID))
    else:
        return redirect("/")












"""
Log out the user by deleting the session token and clearing the session data.

Endpoint: /logout
Method: GET

Returns:
- Redirect to the login page after logging out
"""
@app.route("/logout", methods=["GET"])
def logout():
    delete_from_tokens(f'token="{session["token"]}"')
    session.clear()
    return redirect("/")









"""
Display the home page for city users, showing uploaded files and marketing material.

Endpoint: /city
Method: GET

Requires:
- Valid session token
- User is authenticated as a city

Returns:
- If authentication successful: Rendered HTML template "city/home.html" with user and file information
- If authentication fails or unauthorized: Redirect to the login page
"""
@app.route("/city", methods=["GET"])
def city():
    if token_valid() and "type" in session and session["type"] == "city":
        files = sorted(select_from_files("*", f"cityID = {session['cityID']}"))
        marketingMaterial = [file for file in files if int(file[3]) == 1]
        return render_template('city/home.html', customer_name=select_from_cities("city", f'cityID={session["cityID"]}')[0][0].title(), first_name=session["first_name"], last_name=session["last_name"],files=files, marketingMaterial= marketingMaterial)
    else:
        return redirect("/")










"""
Display the home page for company users, allowing them to select a client and view uploaded files.

Endpoint: /company
Methods: GET, POST

Requires:
- Valid session token
- User is authenticated as a company

Parameters:
- client (int): Default client ID to be displayed (optional, default is 1)

Returns:
- If authentication successful:
    - GET: Rendered HTML template "company/home.html" with client selector and file information
    - POST: Rendered HTML template "company/home.html" with updated client selector and file information
- If authentication fails or unauthorized: Redirect to the login page
"""
@app.route("/company", methods=["GET", "POST"])
def company(client=1):
    form = ClientSelector()
    form.clients.choices = initialize_client_selector()
    if request.method == "POST":
        form.clients.default = request.form.get("clients")
    elif "client" in request.args:
        form.clients.default = request.args["client"]
    else:
        form.clients.default = client
    
    session["cityID"] = form.clients.default
    form.process()
    files = sorted(select_from_files("*", f"cityID = {form.clients.default}"))

    if token_valid() and "type" in session and session["type"] == "company":
        return render_template('company/home.html', form=form, files=files, first_name=session["first_name"], last_name=session["last_name"])
    else:
        return redirect("/")








"""
Redirect to the login page for failed authentication attempts.

Endpoint: /failed_auth
Method: GET

Returns:
- Redirect to the login page, HTTP status code 302
"""
@app.route("/failed_auth", methods=["GET"])
def failed_auth():
    return redirect("/")










#############################
#  Progress Board Endpoints
#############################





"""
Retrieve and return cards associated with the current city user.

Endpoint: /get_cards
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

Returns:
- JSON response containing a list of cards with their IDs, content, and column IDs, HTTP status code 200
"""
@app.route("/get_cards", methods=["POST"])
def get_cards():
    query_results = select_from_cards("relativeID,content,columnID", f'cityID={session["cityID"]}')
    cards = []
    for i in query_results:
        json_object = {"id": i[0], "content": i[1], "column": i[2]}
        cards.append(json_object)
    # print(cards)
    return {"cards": cards}, 200









"""
Add a new card for the current city user.

Endpoint: /add_card
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

JSON Payload:
- "id": ID of the new card
- "text": Content of the new card
- "column": ID of the column to which the new card belongs

Returns:
- Empty response with HTTP status code 200 upon successful addition
"""
@app.route("/add_card", methods=["POST"])
def add_card():
    cardID = request.get_json().get("id")
    content = request.get_json().get("text")
    columnID = request.get_json().get("column")
    insert_into_cards(cardID, content, columnID, session["cityID"])
    return make_response("", 200)









"""
Update the content and column of an existing card for the current city user.

Endpoint: /update_card
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

JSON Payload:
- "id": ID of the card to be updated
- "text": Updated content of the card
- "column": Updated column ID of the card

Returns:
- Empty response with HTTP status code 200 upon successful update
"""
@app.route("/update_card", methods=["POST"])
def update_card():
    # Send this endpoint a card with the same ID, but updated content, and it will replace it.
    cardID = request.get_json().get("id")
    content = request.get_json().get("text")
    columnID = request.get_json().get("column")
    update_in_cards(f'content="{content}",columnID="{columnID}"', f"relativeID={cardID} AND cityID={session['cityID']}")
    return make_response("", 200)









"""
Delete an existing card for the current city user.

Endpoint: /delete_card
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

JSON Payload:
- "id": ID of the card to be deleted
- "text": Content of the card to be deleted (optional)
- "column": Column ID of the card to be deleted (optional)

Returns:
- Empty response with HTTP status code 200 upon successful deletion
"""
@app.route("/delete_card", methods=["POST"])
def delete_card():
    cardID = request.get_json().get("id")
    content = request.get_json().get("text")
    columnID = request.get_json().get("column")
    delete_from_cards(f'relativeID={cardID} AND cityID={session["cityID"]}')
    return make_response("", 200)











#############################
#  Messaging Endpoints
############################# 





"""
Add a new message to the messages database for the current city user.

Endpoint: /add_message
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

JSON Payload:
- "id": ID of the new message
- "content": Content of the new message
- "author": Author of the new message
- "timestamp": Timestamp of the new message

Returns:
- Empty response with HTTP status code 200 upon successful addition
"""
@app.route('/add_message', methods=["POST"])
def add_message():
    messageID = request.get_json().get('id')
    content = request.get_json().get('content')
    author = request.get_json().get('author')
    timestamp = request.get_json().get('timestamp')
    insert_into_messages(messageID, content, session["cityID"], timestamp, author)
    return make_response('',200)








"""
Retrieve and return messages associated with the current city user.

Endpoint: /get_messages
Method: POST

Requires:
- Valid session token
- User is authenticated as a city

Returns:
- JSON response containing a list of messages with their IDs, content, author, and timestamp, HTTP status code 200
"""
@app.route('/get_messages', methods=["POST"])
def get_messages():
    query_results = select_from_messages("relativeID,content,author,timestamp", f'cityID={session["cityID"]}')
    print(query_results)
    messages = []
    for i in query_results:
        json_object = {'id': i[0],'content': i[1],'author': i[2], 'timestamp': i[3]}
        messages.append(json_object)
    return {'messages': messages}, 200









#############################
#  Token Validator
#############################



"""
Check if the current session token is valid by querying the tokens database.

Requires:
- Valid session token stored in the session object

Returns:
- True if the session token is found in the tokens database, False otherwise
"""
def token_valid():
    try:
        query_results = select_from_tokens("token", f'token="{session["token"]}"')
        return True if len(query_results) > 0 else False
    except:
        return False











#  █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗
# ██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║
# ███████║██║  ██║██╔████╔██║██║██╔██╗ ██║
# ██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝

appAdmin = Flask(__name__, template_folder="app/templates", static_folder="app/static")





"""
Retrieve all user and city data for display on the admin page.

Endpoint: /admin
Method: GET

Returns:
- Rendered HTML template "admin/dashboard.html" with user and city data, HTTP status code 200
"""
@appAdmin.route("/", methods=["GET"])
def admin_page():
    """
    Fetchs all users and just displays them on the admin page"""
    user_data = select_from_users("*", None)
    city_data = select_from_cities("*", None)
    users = [
        {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "user_type": user[3],
            "username": user[4],
            "cityID": user[6],
        }
        for user in user_data
    ]
    cities = [
        {"cityID": city[0], "city": city[1], "state": city[2]} for city in city_data
    ]
    return render_template("admin/dashboard.html", users=users, cities=cities)










"""
Create a new user and associated city if necessary, based on form data.

Endpoint: /admin/create_user
Methods: GET (render the form), POST (process form submission)

Requires:
- Form data containing:
    - "first_name": First name of the new user
    - "last_name": Last name of the new user
    - "user_type": Type of the new user
    - "username": Username of the new user
    - "password": Password of the new user
    - "city": City of the new user
    - "state": State of the new user

Returns:
- If POST request:
    - Redirect to the admin page upon successful user and city creation
- If GET request:
    - Render the HTML template "admin/create_user.html" for user input
"""
@appAdmin.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        user_type = request.form["user_type"]
        username = request.form["username"]
        password = request.form["password"]
        city = request.form["city"].lower()
        state = request.form["state"].lower()
        query_results = select_from_cities(
            "cityID", f'city="{city}" AND state="{state}"'
        )
        if len(query_results) == 0:
            print("city does not exist, creating")
            insert_into_cities(city, state)
            query_results = select_from_cities(
                "cityID", f'city="{city}" AND state="{state}"'
            )
        insert_into_users(
            first_name, last_name, user_type, username, password, query_results[0][0]
        )
        return redirect(url_for("admin_page"))
    return render_template("admin/create_user.html")









# ██╗    ██╗███████╗██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗
# ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██║ █╗ ██║█████╗  ██████╔╝    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
# ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
# ╚███╔███╔╝███████╗██████╔╝    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
#  ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝



"""
Run the Flask application for the public page.
"""
def run_public_page():
    app.run(debug=False, port=5000)



"""
Run the Flask application for the admin page.
"""
def run_admin_page():
    appAdmin.run(debug=False, port=8123)


"""
Periodically clean up expired tokens from the tokens database.
"""
def token_watchdog():
    while True:
        # print("Token Cleanup")
        delete_from_tokens(
            f"expire_date<{(datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()}"
        )
        time.sleep(60)



"""
Catches the Ctrl-C Signal in the main thread so that all threads stop at same time.
https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python#1112350
"""
def signal_handler(sig, frame):
    sys.exit(0)


if __name__ == "__main__":
    # Clean up any existing tokens in the tokens database
    delete_from_tokens(None)

    # Create and start threads for the public page, admin page, and token watchdog
    threads.append(threading.Thread(target=run_public_page))
    threads.append(threading.Thread(target=run_admin_page))
    threads.append(threading.Thread(target=token_watchdog))
    for i in threads:
        i.start()

    # Register a signal handler for the SIGINT signal (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
