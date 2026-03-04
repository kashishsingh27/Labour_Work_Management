from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(120), nullable=False)
#    email = db.Column(db.String(120), unique=True, nullable=False)
#    password = db.Column(db.String(200), nullable=False)
#    role = db.Column(db.String(20), nullable=False)  # contractor / labour#
#
#    def __repr__(self):
#        return f"User('{self.username}', '{self.role}')"*/
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50))   # 👈 ADD THIS

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    city = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    wage = db.Column(db.Integer)
    work_type = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contractor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    contractor = db.relationship("User", backref="jobs")   

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    labour_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)

    status = db.Column(db.String(20), default="Pending")

    labour = db.relationship("User", backref="applications")
    job = db.relationship("Job", backref="applications")

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.String(255))

    job_id = db.Column(db.Integer, db.ForeignKey("job.id")) 

    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")
    job = db.relationship("Job") 
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    labour_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    contractor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))

    rating = db.Column(db.Integer)  # 1–5
    review = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    labour = db.relationship("User", foreign_keys=[labour_id])
    contractor = db.relationship("User", foreign_keys=[contractor_id])
    job = db.relationship("Job")    

    
           