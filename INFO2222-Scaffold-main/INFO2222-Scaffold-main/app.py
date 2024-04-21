'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session, redirect, jsonify
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

    if db.validPassword(password) == False:
        return "Error: Password must be at least 8 characters long and contain at least one uppercase letter and one special character"



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
    friends_list = db.get_friends(currentUserName)
    friend_requests_sent = db.retieve_Friend_Requests_Sent(currentUserName)
    print("Friend Requests")
    print(friend_requests)
    print("Friends List")
    print(friends_list)

    print("Current user = " + currentUserName)
    
    return render_template("home.jinja", username=request.args.get("username"), friend_requests=friend_requests, friends=friends_list, friend_requests_sent=friend_requests_sent)




# HERE THE FRIEND REQUESTS ARE HANDLED
@app.route("/add_friend", methods=["POST"])
def add_Friend():
    
    username = request.form.get("username")
    friendsName = request.form.get("friend_username")

    db.sendFriendRequest(username,friendsName)
    friend_requests = db.retieve_Friend_Requests(friendsName)

    print(friend_requests)
    
    return redirect(url_for('home', username=username, friend_requests=friend_requests))
    



    # IT WORKS! but I need to maybe add a sent requests box

@app.route("/accept_friend_request", methods=["POST"])
def accept_friend_request():
    username = request.form.get("username")
    friend = request.form.get("friend_username")
    print("Username:" +username)
    print("Friends name:" +friend)
    # Print returned friend request list
    print(db.acceptFriendRequest(username, friend))
    friend_requests = db.retieve_Friend_Requests(username)
    print(friend_requests)

    return redirect(url_for('home', username=username, friend_requests=friend_requests))


@app.route("/reject_friend_request", methods=["POST"])
def reject_friend_request():
    username = request.form.get("username")
    friend = request.form.get("friend_username")
    print("Username:" +username)
    print("Friends name:" +friend)
    # Print returned friend request list
    print(db.rejectFriendRequest(username, friend))
    friend_requests = db.retieve_Friend_Requests(username)
    print(friend_requests)

    return redirect(url_for('home', username=username, friend_requests=friend_requests))

@app.route("/save_Public_Key", methods=["POST"])
def save_Public_Key():
    
    if not request.is_json:
        return "Error: Not JSON", 400
    
    
    data = request.get_json()
    username = data.get("username")
    
    
    
    if not username:
        print("Error: No username")
        return "Error: No username"
    
    public_key = data.get("publicKey")
    
    if not public_key:
        return "Error: No public key"
    
    
    # update the public key in the database
    update = db.put_public_key(username, public_key)
    
    print(update)
    if update:
        print("Success: Public key updated")
        return "Success: Public key updated"
    else:
        print("Error: Public key not updated")
        return "Error: Public key not updated"
    

    return redirect(url_for('home', username=username))



@app.route("/get_Public_Key/<username>", methods=["GET"])
def get_Public_Key(username):

    print("Username of public get request: " + username)
    public_key = db.get_public_key(username)
    print(public_key)
    
    
    if public_key:
        return jsonify({"public_key": public_key})
    else:
        return jsonify({"error": "Public key not found"}), 404
    
    
@app.route("/get_FriendsList/<username>", methods=["GET"])
def get_FriendsList(username):

    print("Username of friends List: " + username)
    friends_list = db.get_friends(username)
    
    
    
    if friends_list:
        return jsonify({"friends_list": friends_list})
    else:
        return jsonify({"error": "friends list not found"}), 404

if __name__ == '__main__':
    socketio.run(app, ssl_context=('./certs/newCerts2/localhostServer.crt', './certs/newCerts2/localhostServer.key'))
    
    #/usr/local/share/ca-certificates/myCA.crt'

    # pwd: /mnt/c/INFO2222/INFO2222-A2/INFO2222-Scaffold-main/INFO2222-Scaffold-main
    #crt file 
