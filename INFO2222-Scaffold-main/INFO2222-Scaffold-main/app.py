'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session, redirect
from flask_socketio import SocketIO
import db
import secrets


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


    

    # Need to check hash pass here insted    

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    print("salt: " + user.salt)
    
    password = db.hash_password(password,user.salt)
    
    if user.password != password:
        return "Error: Password does not match!"
    
    session['username'] = username


    return url_for('home', username=request.json.get("username"))

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

        # HASH AND SALT PASSWORD
        # Generate a random salt
        salt = secrets.token_hex(16)    
        hashedPassword = db.hash_password(password,salt)

        

        db.insert_user(username, hashedPassword,salt)

        user = db.get_user(username)
        

        print("salt: " + user.salt)
    
        return url_for('home', username=username)
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

    print("IT WORKSKJDJDJDJSAOIDHUFHEWUIH")
    currentUserName = request.args.get("username")
    
    
    friend_requests = db.retieve_Friend_Requests(currentUserName)
    
    return render_template("home.jinja", username=request.args.get("username"), friend_requests=friend_requests)




# HERE THE FRIEND REQUESTS ARE HANDLED
@app.route("/add_friend", methods=["POST"])
def add_Friend():
    
    username = request.form.get("username")
    friendsName = request.form.get("friend_username")

    #print(username)
    #print(friendsName)


    #username = request.json.get("username")
    #friendsName = request.json.get("friendUsername")

    # Print returned friend request list
    print(db.sendFriendRequest(username,friendsName))

    
    return render_template("home.jinja", username=request.args.get("username"))



    # IT WORKS! but I need to maybe add a sent requests box







if __name__ == '__main__':
    socketio.run(app, ssl_context=('/usr/local/share/ca-certificates/myCA.crt', './certs/myCA.key'))
    

    #crt file 
