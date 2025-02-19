import click
from flask import Flask
from flask.cli import with_appcontext
import csv
from os import listdir
from os.path import splitext
from App.database import create_db
from App.main import app, migrate
from App.controllers import ( create_user, get_all_users, get_user )
from App.database import db
from App.models import Programme,User,Profile
from App.controllers import storage
from App.controllers import user_search

@app.cli.command("init")
def initialize():
    create_db(app)
    print('database intialized')

@app.cli.command("create-user")
@click.argument("username")
@click.argument("password")
@click.argument("email")
def create_user_command(username, password, email):
    create_user(username, password, email)
    print(f'{username} created!')

@app.cli.command("delete")
@click.argument("email")
def delete(email):
    User.query.filter_by(email = email).delete()
    db.session.commit()
    print ("deleted user")

@app.cli.command("drop")
def delete_tables():
    db.drop_all()
    db.session.commit()
    print ("dropped tables")

@app.cli.command("get-user")
@click.argument("username")
def get_a_user(username):
    print(get_user(username).profile.programme)

@app.cli.command("get-users")
def get_users():
    print([p.toDict() for p in get_all_users()])

@app.cli.command("search")
@click.argument("name")
def search(name):
    if name.count('_') == 1:
        s = name.split('_')
        print(user_search(s[0]+" "+s[1]))
    else:
        print(user_search(name))
    
@app.cli.command('test')
@click.argument('id')
def testing_relations(id):
    programme = Programme.query.filter_by(id=id).first()
    profiles = programme.profiles.filter(Profile.graduation_year==2022).all()
    print([p.first_name for p in profiles])
    

def programmes(): 
    with open(r'App/programs.csv') as file:
        fieldnames = ['Programme','Degree','Department','Faculty']
        reader = csv.DictReader(file,fieldnames=fieldnames)
        for row in reader:
            pro = Programme(
                name = row['Programme'] ,
                degree =row['Degree']  ,
                department =row['Department'] ,
                faculty =row['Faculty']
            )
            db.session.add(pro)
            db.session.commit()
        print( 'programmes added')

def  userprofile():
    with open(r'App/user.csv') as file:
        fieldnames = ['Username','First Name','Last Name','Email','Password','Programme','Degree','Department','Faculty','Graduation Year','Facebook','Instagram','LinkedIn']
        reader = csv.DictReader(file,fieldnames=fieldnames)
        for row in reader:
            newUser = create_user(row['Username'],row['Password'],row['Email'])
            if newUser:
                user = User.query.filter_by(email = row['Email']).first()
                prog = Programme.query.filter_by(name = row['Programme'], degree = row['Degree']).first()
                profile = Profile(
                    uid = user.id,
                    first_name = row['First Name'],
                    last_name = row['Last Name'],
                    programme_id = prog.id,
                    graduation_year = row['Graduation Year'],
                    facebook = row['Facebook'],
                    instagram =row['Instagram'],
                    linkedin = row['LinkedIn']
                )
                db.session.add(profile)
                db.session.commit()
    print ("users added")

def propics():
    images = listdir('Userpics')
    names = []
    print(len(images))
    for image in images:
        imgName = splitext(image)
        names.append(imgName[0])
    for name in names:
        parts = name.split()
        puser = Profile.query.filter_by(first_name = parts[0], last_name = parts[1]).first()
        try:
            token = storage.child(f'{puser.uid}.jpg').put(f'Userpics/{name}.jpg')
            purl = storage.child(f'{puser.uid}.jpg').get_url(token['downloadTokens'])
            puser.url = f"{purl}"
            db.session.commit()
        except:
            print(parts[0], parts[1])
    print("images added")


@app.cli.command("populate-db")
def populate():
    print("populating...")
    # programmes()
    # userprofile()
    # propics()
    print("populating completed")

@app.cli.command("rollback")
def rollback():
    db.session.rollback()