# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
import firebase_admin
from firebase_admin import credentials





db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove() 


def create_app(config):
    app = Flask(__name__)
     # Your Firebase configuration
    firebase_config = {
        "apiKey": "AIzaSyACI4bAOfMJZtPpXyk9SQC51yhyRPssveM",
        "authDomain": "orequalityquantifier.firebaseapp.com",
        "databaseURL": "https://orequalityquantifier-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "orequalityquantifier",
        "storageBucket": "orequalityquantifier.appspot.com",
        "messagingSenderId": "242834658088",
        "appId": "1:242834658088:web:5343b6223411aa4ebeb61d",
        "measurementId": "G-KQWH6YV66M"
    }

    # Initialize Firebase
    cred = credentials.Certificate("apps/key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_config["databaseURL"],
        "apiKey": firebase_config["apiKey"],
        "authDomain": firebase_config["authDomain"],
        "projectId": firebase_config["projectId"],
        "storageBucket": firebase_config["storageBucket"],
        "messagingSenderId": firebase_config["messagingSenderId"],
        "appId": firebase_config["appId"],
        "measurementId": firebase_config["measurementId"]
    })
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
