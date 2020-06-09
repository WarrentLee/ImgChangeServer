from flask import Flask
from database.model import db
import os, json
from config import Config


def create_app(name):
    app = Flask(name, template_folder='../templates')
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(app.root_path, 'data.db'))
    print("Database Directory:",  os.getenv('DATABASE_URL'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + Config.DATABASE_DIRECTORY)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "asfnsdjnsdlflasdkc553d3s1"
    db.app = app
    db.init_app(app)
    return app



