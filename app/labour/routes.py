from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models import Job, Application, Rating

from flask_mail import Message
from app.extensions import mail

labour = Blueprint("labour", __name__, url_prefix="/labour")


@labour.route("/dashboard")
@login_required
def labour_dashboard():

    if current_user.role != "labour":
        return redirect(url_for("auth.login"))

    jobs_completed = Application.query.filter_by(
        labour_id=current_user.id,
        status="Accepted"
    ).count()

    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(
        labour_id=current_user.id
    ).scalar()

    avg_rating = round(avg_rating,2) if avg_rating else 0

    return render_template(
        "labour/dashboard.html",
        jobs_completed=jobs_completed,
        avg_rating=avg_rating
    )


@labour.route("/jobs")
@login_required
def view_jobs():

    if current_user.role != "labour":
        return redirect(url_for("auth.login"))

    city = request.args.get("city")
    pincode = request.args.get("pincode")
    min_wage = request.args.get("min_wage")
    work_type = request.args.get("work_type")

    query = Job.query

    if city:
        query = query.filter(Job.city.ilike(f"%{city}%"))

    if pincode:
        query = query.filter(Job.pincode == pincode)

    if min_wage:
        query = query.filter(Job.wage >= int(min_wage))

    if work_type:
        query = query.filter(Job.work_type == work_type)

    jobs = query.order_by(Job.created_at.desc()).all()

    return render_template("labour/jobs.html", jobs=jobs)


@labour.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):

    if current_user.role != "labour":
        flash("Only labour can apply for jobs.")
        return redirect(url_for("labour.view_jobs"))

    job = Job.query.get_or_404(job_id)

    existing_application = Application.query.filter_by(
        labour_id=current_user.id,
        job_id=job.id
    ).first()

    if existing_application:
        flash("You already applied to this job.")
        return redirect(url_for("labour.view_jobs"))

    application = Application(
        labour_id=current_user.id,
        job_id=job.id
    )

    db.session.add(application)
    db.session.commit()

    msg = Message(
    subject="New Job Application Received",
    recipients=[job.contractor.email]
)

    msg.body = f"""
    Hello {job.contractor.username},

    You have received a new application for your job:

    Job Title: {job.title}

    Applicant: {current_user.username}

    Login to view and manage applications.

    LWMS Team
    """

    mail.send(msg)    

    flash("Application submitted successfully!")

    return redirect(url_for("labour.view_jobs"))


@labour.route("/job/<int:job_id>/simple")
@login_required
def view_single_job(job_id):

    job = Job.query.get_or_404(job_id)

    return render_template("labour/single_job.html", job=job)

@labour.route("/job/<int:job_id>")
@login_required
def job_detail(job_id):

    job = Job.query.get_or_404(job_id)

    return render_template("labour/job_details.html", job=job)