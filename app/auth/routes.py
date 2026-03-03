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
        city = request.form.get("city")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username=username, email=email, password=hashed_pw, role=role, city=city)
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
        pincode = request.form.get("pincode")
        wage = request.form.get("wage")
        work_type = request.form.get("work_type")

        job = Job(
            title=title,
            description=description,
            city=city,
            pincode=pincode,
            wage=wage,
            work_type=work_type,
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
        flash("Only labour can apply for jobs.")
        return redirect(url_for("auth.view_jobs"))

    job = Job.query.get_or_404(job_id)

    # Check duplicate
    existing_application = Application.query.filter_by(
        labour_id=current_user.id,
        job_id=job.id
    ).first()

    if existing_application:
        flash("You have already applied to this job.")
        return redirect(url_for("auth.view_jobs"))

    application = Application(
        labour_id=current_user.id,
        job_id=job.id
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully!")
    return redirect(url_for("auth.view_jobs"))    


@auth.route("/contractor/applications")
@login_required
def view_applications():

    if current_user.role != "contractor":
        flash("Access denied.")
        return redirect(url_for("auth.login"))

    # Get contractor jobs
    jobs = Job.query.filter_by(contractor_id=current_user.id).all()

    # Collect applications
    applications = []

    for job in jobs:
        for app in job.applications:
            applications.append(app)

    return render_template(
        "contractor/applications.html",
        applications=applications
    )

@auth.route("/application/<int:app_id>/accept")
@login_required
def accept_application(app_id):

    application = Application.query.get_or_404(app_id)

    if current_user.id != application.job.contractor_id:
        flash("Unauthorized action.")
        return redirect(url_for("auth.contractor_dashboard"))

    application.status = "Accepted"
    db.session.commit()

    flash("Application accepted.")
    return redirect(url_for("auth.view_applications"))


@auth.route("/application/<int:app_id>/reject")
@login_required
def reject_application(app_id):

    application = Application.query.get_or_404(app_id)

    if current_user.id != application.job.contractor_id:
        flash("Unauthorized action.")
        return redirect(url_for("auth.contractor_dashboard"))

    application.status = "Rejected"
    db.session.commit()

    flash("Application rejected.")
    return redirect(url_for("auth.view_applications"))

