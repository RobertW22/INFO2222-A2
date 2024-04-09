'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

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
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
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


    
def sendFriendRequest(username,target):

    targetAccount = get_user(target)
    print(target)
    
    if not targetAccount:
        return "friend not found"

    targetAccount.friendRequests.append(username)

    #for testing
    return targetAccount.friendRequests
