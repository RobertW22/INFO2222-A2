'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request, session
from crypto_utils import generate_shared_secret, verify_mac

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")

    # For user online status
    emit("user_connected", username, broadcast=True)

    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    
     # For user not online status
    emit("user_disconnected", username, broadcast=True)

    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, encrypted_message, mac, room_id):
    print("Received 'send' event:")
    print("Username:", username)
    print("Encrypted Message:", encrypted_message)
    print("MAC:", mac)
    print("Room ID:", room_id)

    # Retrieve conversation from database
    conversation = db.get_conversation(username, room_id)
    if conversation is None:
        # Handle case when conversation is not found
        print("Conversation not found for username:", username, "and room ID:", room_id)
        return

    shared_secret = bytes.fromhex(conversation.shared_secret)

    # Verify message integrity
    message = encrypted_message.encode()
    is_valid = verify_mac(message, bytes.fromhex(mac), shared_secret)
    if is_valid:
        print("Emitting 'incoming' event:", (username, encrypted_message, mac)) # Debugging: Log data being emitted
        emit("incoming", (username, encrypted_message, mac), to=room_id)
    else:
        # Handle case when message integrity is compromised
        print("Message integrity compromised!")
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name, public_key):
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"

    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    shared_secret = generate_shared_secret(sender.private_key.encode(), public_key.encode())
    db.insert_conversation(sender_name, receiver_name, shared_secret.hex())

    room_id = room.get_room_id(receiver_name)

    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
    else:
        room_id = room.create_room(sender_name, receiver_name)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)

    print("room_id:", room_id)
    print("receiver.public_key:", receiver.public_key)
    print("shared_secret:", shared_secret)
    response = {
        "room_id": room_id,
        "receiver_public_key": receiver.public_key,
        "shared_secret_key": shared_secret.hex()
    }
    print("response:", response)
    return response

@socketio.on('request_public_key')
def handle_request_public_key(username):
    print(f"Received request_public_key event for username: {username}")
    user = db.get_user(username)
    if user:
        print(f"User found: {user.username}")
        print(f"Public key: {user.public_key}")
        print(f"Type of public key: {type(user.public_key)}")
        emit('public_key_response', user.public_key, room=request.sid)
    else:
        print(f"User not found: {username}")
        emit('public_key_response', 'User not found', room=request.sid)

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)