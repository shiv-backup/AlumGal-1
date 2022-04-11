from App.models import User
from App.database import db
from flask_sqlalchemy import IntegrityError

def get_all_users():
    return User.query.all()

def get_user(username):
    return User.query.get(username)

def create_user(username, password, email):
    newuser = User(username=username, password=password, email=email)
    try:
        db.session.add(newuser)
        db.session.commit()
        return True
    except IntegrityError:
        return False


def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.toDict() for user in users]
    return users