from flask import Flask,request,render_template
import sqlite3
import hashlib

# Flask object setup
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')


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

@app.route('/', methods=["GET"])
def base_page():
    return render_template('login.html')


@app.route('/admin_page', methods=["GET"])
def admin_page():
    return render_template('admin/create_user.html')

@app.route('/create_user', methods=["GET"])
def create_user():
    users_cursor = users_connection.cursor()
    query = f'INSERT INTO users(id,first_name,last_name,user_type,username,password) VALUES (NULL,"Test","User","client","tuser123","{hashlib.sha256(str.encode("mypassword"+"Alittlebitofsaltandpepper.")).hexdigest()}")'
    users_connection.execute(query)
    users_connection.commit()
    users_cursor.close()
    return render_template('admin/dashboard.html')


@app.route('/auth', methods=["GET"])
def auth():
    users_cursor = users_connection.cursor()
    password = request.args.get('pass')
    username = request.args.get('user')
    query = f'SELECT user_type FROM users WHERE username = "{username}" AND password = "{hashlib.sha256(str.encode(password+"Alittlebitofsaltandpepper.")).hexdigest()}"'
    query_results=users_cursor.execute(query).fetchall()
    users_cursor.close()
    # print(query_results)
    if(len(query_results) > 0):
        if(query_results[0][0] == "client"):
            return render_template('city/home.html')
        else:
            return render_template('company/home.html')

if __name__ == "__main__":
    app.run(debug=False)