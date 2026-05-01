from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User, Notification, Rating, Job, Application
from app.extensions import db, bcrypt, mail
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import func
from flask_mail import Message
import logging
import re



# VALIDATION HELPERS
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_not_empty(value):
    return value and value.strip() != ""



# BLUEPRINT
auth = Blueprint("auth", __name__)


# HOME
@auth.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "contractor":
            return redirect(url_for("contractor.contractor_dashboard"))
        else:
            return redirect(url_for("labour.labour_dashboard"))
    return render_template("index.html")


# REGISTER
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role")
        city = request.form.get("city", "").strip()
        phone = request.form.get("phone", "").strip()

        #  VALIDATION
        if not is_valid_email(email):
            flash("Invalid email format", "danger")
            logging.warning(f"Invalid email attempt: {email}")
            return redirect(url_for("auth.register"))

        if not is_not_empty(username):
            flash("Username cannot be empty", "danger")
            return redirect(url_for("auth.register"))

        if not is_not_empty(password):
            flash("Password cannot be empty", "danger")
            return redirect(url_for("auth.register"))

        # DUPLICATE CHECK
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            logging.warning(f"Duplicate registration attempt: {email}")
            return redirect(url_for("auth.register"))

        #  CREATE USER
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username,
            email=email,
            password=hashed_pw,
            role=role,
            city=city,
            phone=phone
        )

        db.session.add(user)
        db.session.commit()

        logging.info(f"New user registered: {email}")

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")



# LOGIN
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        #  BASIC VALIDATION
        if not is_valid_email(email):
            flash("Invalid email format", "danger")
            return redirect(url_for("auth.login"))

        if not is_not_empty(password):
            flash("Password cannot be empty", "danger")
            return redirect(url_for("auth.login"))

        logging.info(f"Login attempt: {email}")

        user = User.query.filter_by(email=email).first()

        #  AUTH CHECK
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            logging.info(f"Login success: {email}")

            if user.role == "contractor":
                return redirect(url_for("contractor.contractor_dashboard"))
            else:
                return redirect(url_for("labour.labour_dashboard"))

        #  FAILED LOGIN
        logging.warning(f"Failed login attempt: {email}")
        flash("Invalid email or password", "danger")

    return render_template("login.html")



# LOGOUT
@auth.route("/logout")
@login_required
def logout():
    logging.info(f"User logged out: {current_user.email}")
    logout_user()
    return redirect(url_for("auth.login"))


# NOTIFICATION
@auth.route("/notifications")
@login_required
def view_notifications():

    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()

    # Mark as read
    for n in notifications:
        n.is_read = True

    db.session.commit()

    unread_count = sum(1 for n in notifications if not n.is_read)
    accepted_count = sum(1 for n in notifications if 'accepted' in n.message.lower())
    rejected_count = sum(1 for n in notifications if 'rejected' in n.message.lower())

    logging.info(f"User {current_user.id} viewed notifications")

    return render_template(
        "notifications.html",
        notifications=notifications,
        unread_count=unread_count,
        accepted_count=accepted_count,
        rejected_count=rejected_count
    )

from flask_migrate import upgrade

@auth.route("/setup-db")
def setup_db():
    try:
        upgrade()
        return "Database migrated successfully!"
    except Exception as e:
        return str(e)