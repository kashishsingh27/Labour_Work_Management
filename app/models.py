from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # contractor / labour

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    contractor = db.relationship('User', backref='jobs')

    def __repr__(self):
        return f"Job('{self.title}', '{self.city}')"    

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    labour_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship('Job', backref='applications')
    labour = db.relationship('User')        