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





def sendFriendRequest(username,target):


    with Session(engine) as session:
        targetAccount = session.get(User, target)
        if not targetAccount:
            return "friend not found"


        #add test friends
        
        if targetAccount.friendRequests == "":
            targetAccount.friendRequests = username
        else:
            targetAccount.friendRequests = targetAccount.friendRequests + "," + username


        returnList = targetAccount.friendRequests.split(",")
        session.commit()


    return returnList


# Simply returns the friend requests of a user and displays on the HTML page
def retieve_Friend_Requests(username):

    with Session(engine) as session:
        user = session.get(User, username)
        if not user:
            return "User not found"
        return user.friendRequests.split(",")

def get_friends(username):
    with Session(engine) as session:
        user = session.get(User, username)
        if not user:
            return "User not found"
        return user.friends.split(",")
  
def acceptFriendRequest(username, friendName):
    with Session(engine) as session:

        user = session.get(User, username)
        friend = session.get(User, friendName)

        if not user or not friend:
            return "User or friend not found"
        
        # Add the friend to the user's friend list
        if user.friends == "":
            user.friends = friendName
        else:
            user.friends = user.friends + "," + friendName

        # Add the user to the friend's friend list
        if friend.friends == "":
            friend.friends = username
        else:
            friend.friends = friend.friends + "," + username


        # later to do remove from sent friends list

        # Remove the friend request
        friendRequests = user.friendRequests.split(",")
        friendRequests.remove(friendName)

        user.friendRequests = ",".join(friendRequests)

        session.commit()
        
        return user.friends.split(",")

    
    
    
    
    


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

