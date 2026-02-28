from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User
from app.extensions import db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required

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

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username=username, email=email, password=hashed_pw, role=role)
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
                return redirect(url_for("auth.contractor_dashboard"))
            else:
                return redirect(url_for("auth.labour_dashboard"))

        flash("Login unsuccessful", "danger")

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/contractor/dashboard")
@login_required
def contractor_dashboard():
    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("contractor/dashboard.html")


@auth.route("/labour/dashboard")
@login_required
def labour_dashboard():
    if current_user.role != "labour":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("labour/dashboard.html")