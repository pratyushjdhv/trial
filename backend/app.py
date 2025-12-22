import os
from flask_cors import CORS
from flask import Flask
from model import db  
from waitress import serve

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'event.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
    

import routes  # Import routes after app and db are set up

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for our data models
    serve(app, host='0.0.0.0', port=5000, threads=12)