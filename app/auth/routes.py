from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User
from app.extensions import db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Job
from app.models import Application

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

@auth.route("/contractor/post-job", methods=["GET", "POST"])
@login_required
def post_job():
    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        city = request.form.get("city")

        job = Job(
            title=title,
            description=description,
            city=city,
            contractor=current_user
        )

        db.session.add(job)
        db.session.commit()

        flash("Job posted successfully!", "success")
        return redirect(url_for("auth.contractor_dashboard"))

    return render_template("contractor/post_job.html")

@auth.route("/jobs")
@login_required
def view_jobs():
    if current_user.role != "labour":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    city = request.args.get("city")

    if city:
        jobs = Job.query.filter(Job.city.ilike(f"%{city}%")).order_by(Job.created_at.desc()).all()
    else:
        jobs = Job.query.order_by(Job.created_at.desc()).all()

    return render_template("labour/jobs.html", jobs=jobs)

@auth.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):
    if current_user.role != "labour":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    existing_application = Application.query.filter_by(
        job_id=job_id,
        labour_id=current_user.id
    ).first()

    if existing_application:
        flash("You already applied for this job.", "info")
        return redirect(url_for("auth.view_jobs"))

    application = Application(
        job_id=job_id,
        labour_id=current_user.id
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully!", "success")
    return redirect(url_for("auth.view_jobs"))    

@auth.route("/contractor/applications/<int:job_id>")
@login_required
def view_applications(job_id):
    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    job = Job.query.get_or_404(job_id)

    if job.contractor_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("auth.contractor_dashboard"))

    return render_template("contractor/applications.html", job=job)