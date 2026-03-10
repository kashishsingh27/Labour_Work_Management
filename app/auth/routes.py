from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User, Notification ,Rating
from app.extensions import db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Job
from app.models import Application
from sqlalchemy import func
from flask_mail import Message
from app.extensions import mail

auth = Blueprint("auth", __name__)

@auth.route("/")
def home():
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        city = request.form.get("city")
        phone = request.form.get("phone")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("auth.register"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username=username, email=email, password=hashed_pw, role=role, city=city ,phone=phone)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            if user.role == "contractor":
                return redirect(url_for("contractor.contractor_dashboard"))
            else:
                return redirect(url_for("labour.labour_dashboard"))

        flash("Login unsuccessful", "danger")

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/notifications")
@login_required
def view_notifications():

    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()

    # Auto mark as read
    for n in notifications:
        n.is_read = True

    db.session.commit()

    return render_template(
        "notifications.html",
        notifications=notifications
    )


