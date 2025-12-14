from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    total_score = db.Column(db.Integer, default=0)
    
    # Track when they joined the event (for time-based scoring)
    event_start_time = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to access their progress easily
    progress = db.relationship('UserProgress', backref='user', lazy=True)

    # This is just a helper to print the user nicely
    def __repr__(self):
        return f'<User {self.username}>'
    

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    
    probes_used = db.Column(db.Integer, default=0)
    is_solved = db.Column(db.Boolean, default=False)
    

    tests_passed = db.Column(db.Integer, default=0) # Tracks how many hidden tests they passed
    solved_at = db.Column(db.DateTime) # Tracks LAST successful submission time


class ProbeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    input_val = db.Column(db.String(50))
    output_val = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)