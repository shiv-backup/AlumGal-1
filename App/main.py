import os
from flask import Flask,flash,redirect,url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import timedelta

from App.database import init_db, get_migrate

from App.controllers import (
    setup_jwt,
    login_manager
)

from App.views import (
    user_views,
    api_views
)

views = [
    user_views,
    api_views
]
UPLOAD_FOLDER = ".\images"
def add_views(app, views):
    for view in views:
        app.register_blueprint(view)

def loadConfig(app, config):
    app.config['ENV'] = os.environ.get('ENV', 'DEVELOPMENT')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if app.config['ENV'] == "DEVELOPMENT":
        app.config.from_object('App.config')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['JWT_EXPIRATION_DELTA'] =  timedelta(days=int(os.environ.get('JWT_EXPIRATION_DELTA')))
        app.config['DEBUG'] = os.environ.get('ENV').upper() != 'PRODUCTION'
        app.config['ENV'] = os.environ.get('ENV')
    for key, value in config.items():
        app.config[key] = config[key]

def create_app(config={}):
    app = Flask(__name__, static_url_path='/static')
    login_manager.init_app(app)
    CORS(app)
    loadConfig(app, config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)
    add_views(app, views)
    init_db(app)
    setup_jwt(app)
    app.app_context().push()
    return app

app = create_app()
migrate = get_migrate(app)

@app.errorhandler(404)
def page_not_found(error):
    if error == 404:
        flash('404 page not found')
    return redirect(url_for('user_views.home'))