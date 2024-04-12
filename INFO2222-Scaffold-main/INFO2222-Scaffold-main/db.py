'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *
import hashlib

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    



#get request to get all the friends of a user
#there is some fuction that gets posts requests ..
def add_friend(current_user, friend_username):
    with Session(engine) as session:
        # Query user object from the database
        user = session.get(User, current_user)
        friend = session.get(User, friend_username)
        
        if not user:
            raise ValueError("User not found")
        
        if not friend:
            raise ValueError("Friend not found")
        
        # Add friend to user's friends list
        if user.friends:

            if friend_username in user.friends:
                return "Friend already added"
            else:
                user.friends.append(friend_username)
        

        
        # Add user to friend's friends list (bidirectional)
        if friend.friends:
            if current_user in friend.friends:
                return "Friend already added"
            else:
                friend.friends.append(current_user)
        

        session.commit()


# Send a friend request to a user 
def sendFriendRequest(username,target):

    targetAccount = get_user(target)
    
    
    if not targetAccount or targetAccount == None or targetAccount == "":
        return "friend not found"

    targetAccount.friendRequests.append(username)


    #for testing
    return targetAccount.friendRequests

# Simply returns the friend requests of a user and displays on the HTML page
def retieve_Friend_Requests(username):

    user = get_user(username)

    print(user.friendRequests)
    return user.friendRequests


# Used for registering
def hash_password(password, salt):

    # Hash and salt the password
    saltedPass = salt + password

    hashedPassword = hashlib.sha256(saltedPass.encode()).hexdigest()

    return hashedPassword

# Used for logging in
def check_hashedpassword(username, password):
    user = get_user(username)

    saltedPass = user.salt + password
    hashedPassword = hashlib.sha256(saltedPass.encode()).hexdigest()

    return hashedPassword

def add_salt(username, salt):
    user = get_user(username)
    user.salt = salt

