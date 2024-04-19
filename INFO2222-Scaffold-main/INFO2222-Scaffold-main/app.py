'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, jsonify, render_template, request, abort, url_for, session, redirect
from flask_socketio import SocketIO
import db
import secrets
from crypto_utils import generate_rsa_keys

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    # Get the stored hashed password and salt from user object
    stored_hashed_password = user.password
    stored_salt = user.salt

    # Hash entered password using stored salt
    entered_hashed_password = db.hash_password(password, stored_salt)
    
    if stored_hashed_password != entered_hashed_password:
        return "Error: Password does not match!"
    
    session['username'] = username

    return jsonify(url=url_for('home', username=username), public_key=user.public_key, private_key=user.private_key)

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    if db.get_user(username) is None:
        # Generate RSA key pair
        private_key, public_key = generate_rsa_keys()

        # Generate a random salt
        salt = secrets.token_hex(16)    
        hashedPassword = db.hash_password(password, salt)

        db.insert_user(username, hashedPassword, salt, public_key.decode(), private_key.decode())
    
        return jsonify(url=url_for('home', username=username), public_key=public_key.decode(), private_key=private_key.decode())
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    return render_template("home.jinja", username=request.args.get("username"))

if __name__ == '__main__':
    socketio.run(app)
    
    #, ssl_context=('/usr/local/share/ca-certificates/myCA.crt', './certs/myCA.key')

    #crt file 
