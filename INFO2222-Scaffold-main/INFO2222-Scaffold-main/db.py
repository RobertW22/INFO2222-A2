'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine, or_
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
def insert_user(username: str, password: str, salt: str, public_key: str, private_key: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt, public_key=public_key, private_key=private_key)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.query(User).filter_by(username=username).first()

# takes a User object and updates it in database
def update_user(user):
    with Session(engine) as session:
        session.merge(user)
        session.commit()

def hash_password(password, salt):
    hashedPassword = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashedPassword

def insert_conversation(user1, user2, shared_secret):
    with Session(engine) as session:
        conversation = Conversation(user1_id=user1, user2_id=user2, shared_secret=shared_secret)
        session.add(conversation)
        session.commit()

def get_conversation(username, room_id):
    with Session(engine) as session:
        conversation = session.query(Conversation).filter(
            or_(Conversation.user1_id == username, Conversation.user2_id == username),
            Conversation.id == room_id
        ).first()
        return conversation