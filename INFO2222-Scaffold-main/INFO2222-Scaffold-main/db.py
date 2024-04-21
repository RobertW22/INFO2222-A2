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
    
# puts public key in the user table
def put_public_key(username: str, public_key: str):
    with Session(engine) as session:
        user = session.get(User, username)
        
        if user:
        
            user.publicKey = public_key
            
            savedKey = user.publicKey
            
            session.commit()
            
    return savedKey

def get_public_key(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        
        if user:
            return user.publicKey
        else:
            return "User not found"

#get request to get all the friends of a user
#there is some fuction that gets posts requests ..





def sendFriendRequest(username,target):


    with Session(engine) as session:
        targetAccount = session.get(User, target)
        userSender = session.get(User, username)
        if not targetAccount:
            return "friend not found"
        
        if target == username:
            return "You can't send a friend request to yourself"
        
        if target in userSender.friends.split(","):
            return "You are already friends with this user"
        
        if target in userSender.friendRequests.split(","):
            return "You have already sent a friend request to this user"


        #add test friends
        
        if targetAccount.friendRequests == "":
            targetAccount.friendRequests = username
        else:
            targetAccount.friendRequests = targetAccount.friendRequests + "," + username


        if userSender.friendRequestsSent == "":
            userSender.friendRequestsSent = target
        else:
            userSender.friendRequestsSent = userSender.friendRequestsSent + "," + target

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
    
def retieve_Friend_Requests_Sent(username):
    
        with Session(engine) as session:
            user = session.get(User, username)
            if not user:
                return "User not found"
            return user.friendRequestsSent.split(",")
        

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

        # Remove the sent friend request
        friendRequestsSent = friend.friendRequestsSent.split(",")
        friendRequestsSent.remove(username)

        friend.friendRequestsSent = ",".join(friendRequestsSent)


        session.commit()
        
        return user.friends.split(",")

def rejectFriendRequest(username, friendName):
    with Session(engine) as session:
        user = session.get(User, username)
        friend = session.get(User, friendName)

        if not user or not friend:
            return "User or friend not found"

        # Remove the friend request
        friendRequests = user.friendRequests.split(",")
        friendRequests.remove(friendName)

        user.friendRequests = ",".join(friendRequests)

        # Remove the sent friend request
        friendRequestsSent = friend.friendRequestsSent.split(",")
        friendRequestsSent.remove(username)

        friend.friendRequestsSent = ",".join(friendRequestsSent)

        session.commit()
        
        return user.friendRequests.split(",")
    
    
    
    



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

# checks password validity for min 8 chars, 1 digit, 1 uppercase
def validPassword(password):
    if len(password) < 8:
        return False
    # Upper case
    if not any(char.isupper() for char in password):
        return False
    # specical character
    specialChars = "!@#$%^&*()-+"
    if not any(char in specialChars for char in password):
        return False
    
    return True

