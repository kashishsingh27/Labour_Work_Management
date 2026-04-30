from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db, mail
from app.models import Job, Application, Rating, User
from flask_mail import Message
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
import logging


labour = Blueprint("labour", __name__, url_prefix="/labour")


# =========================
# DASHBOARD
# =========================
@labour.route("/dashboard")
@login_required
def labour_dashboard():

    if current_user.role != "labour":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    logging.info(f"Labour dashboard accessed: user {current_user.id}")

    total_applications = Application.query.filter_by(labour_id=current_user.id).count()
    pending_count = Application.query.filter_by(labour_id=current_user.id, status="Pending").count()
    accepted_count = Application.query.filter_by(labour_id=current_user.id, status="Accepted").count()
    rejected_count = Application.query.filter_by(labour_id=current_user.id, status="Rejected").count()

    recent_applications = Application.query \
        .filter_by(labour_id=current_user.id) \
        .order_by(Application.created_at.desc()) \
        .limit(5).all()

    avg_rating = db.session.query(func.avg(Rating.rating)) \
        .filter_by(labour_id=current_user.id).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating else 0

    # Weekly activity
    today = datetime.utcnow().date()
    weekly_labels = []
    weekly_counts = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        count = Application.query.filter(
            Application.labour_id == current_user.id,
            db.func.date(Application.created_at) == day
        ).count()

        weekly_labels.append(day.strftime('%a'))
        weekly_counts.append(count)

    available_jobs = Job.query.count()

    nearby_jobs = Job.query.filter(
        Job.city.ilike(f"%{current_user.city}%")
    ).order_by(Job.created_at.desc()).limit(6).all() if current_user.city else []

    return render_template(
        "labour/dashboard.html",
        total_applications=total_applications,
        pending_count=pending_count,
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        recent_applications=recent_applications,
        weekly_labels=weekly_labels,
        weekly_counts=weekly_counts,
        available_jobs=available_jobs,
        nearby_jobs=nearby_jobs,
        avg_rating=avg_rating,
    )


# =========================
# VIEW JOBS (FILTERING)
# =========================
@labour.route("/jobs")
@login_required
def view_jobs():

    if current_user.role != "labour":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    city = request.args.get("city", "").strip()
    pincode = request.args.get("pincode", "").strip()
    min_wage = request.args.get("min_wage", "").strip()
    work_type = request.args.get("work_type", "").strip()

    query = Job.query

    # ✅ SAFE FILTERS
    if city:
        query = query.filter(Job.city.ilike(f"%{city}%"))

    if pincode:
        if pincode.isdigit():
            query = query.filter(Job.pincode == pincode)
        else:
            flash("Invalid pincode format", "danger")

    if min_wage:
        if min_wage.isdigit():
            query = query.filter(Job.wage >= int(min_wage))
        else:
            flash("Minimum wage must be a number", "danger")

    if work_type:
        query = query.filter(Job.work_type == work_type)

    jobs = query.order_by(Job.created_at.desc()).all()

    work_types = db.session.query(distinct(Job.work_type)) \
        .filter(Job.work_type != None, Job.work_type != "") \
        .order_by(Job.work_type) \
        .all()

    work_types = [wt[0] for wt in work_types]

    logging.info(f"User {current_user.id} viewed jobs with filters")

    return render_template("labour/jobs.html", jobs=jobs, work_types=work_types)


# =========================
# APPLY JOB
# =========================
@labour.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):

    if current_user.role != "labour":
        flash("Only labour can apply for jobs.", "danger")
        return redirect(url_for("labour.view_jobs"))

    job = Job.query.get_or_404(job_id)

    existing_application = Application.query.filter_by(
        labour_id=current_user.id,
        job_id=job.id
    ).first()

    if existing_application:
        flash("You already applied to this job.", "warning")
        logging.warning(f"Duplicate application attempt: user {current_user.id}, job {job.id}")
        return redirect(url_for("labour.view_jobs"))

    application = Application(
        labour_id=current_user.id,
        job_id=job.id
    )

    db.session.add(application)
    db.session.commit()

    logging.info(f"User {current_user.id} applied to job {job.id}")

    # ✅ SAFE EMAIL SEND
    try:
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
        logging.info(f"Email sent to contractor {job.contractor.email}")

    except Exception as e:
        logging.warning(f"Email failed for job {job.id}: {str(e)}")

    flash("Application submitted successfully!", "success")
    return redirect(url_for("labour.view_jobs"))


# =========================
# VIEW SINGLE JOB
# =========================
@labour.route("/job/<int:job_id>/simple")
@login_required
def view_single_job(job_id):

    job = Job.query.get_or_404(job_id)

    logging.info(f"User {current_user.id} viewed job {job.id}")

    return render_template("labour/single_job.html", job=job)

# =========================
# JOB DETAIL (FULL VIEW)
# =========================
@labour.route("/job/<int:job_id>")
@login_required
def job_detail(job_id):

    job = Job.query.get_or_404(job_id)

    logging.info(f"User {current_user.id} viewed full job {job.id}")

    return render_template("labour/job_details.html", job=job)


# =========================
# LABOUR PROFILE VIEW
# =========================
@labour.route("/profile/<int:user_id>")
@login_required
def labour_profile(user_id):

    labour_user = User.query.get_or_404(user_id)

    if labour_user.role != "labour":
        flash("User is not a labour worker.", "danger")
        return redirect(url_for("auth.home"))

    logging.info(f"Profile viewed: user {current_user.id} -> labour {labour_user.id}")

    completed_applications = Application.query.filter_by(
        labour_id=labour_user.id,
        status="Accepted"
    ).order_by(Application.id.desc()).all()

    ratings = Rating.query.filter_by(
        labour_id=labour_user.id
    ).order_by(Rating.created_at.desc()).all()

    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(
        labour_id=labour_user.id
    ).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating else 0

    jobs_completed = len(completed_applications)
    total_applications = Application.query.filter_by(
        labour_id=labour_user.id
    ).count()

    # Rating distribution
    star_distribution = []
    for star in range(1, 6):
        count = Rating.query.filter_by(
            labour_id=labour_user.id,
            rating=star
        ).count()
        star_distribution.append(count)

    return render_template(
        "labour/labour_profile.html",
        labour_user=labour_user,
        completed_applications=completed_applications,
        ratings=ratings,
        avg_rating=avg_rating,
        jobs_completed=jobs_completed,
        total_applications=total_applications,
        rating_count=len(ratings),
        star_distribution=star_distribution
    )


# =========================
# EDIT PROFILE
# =========================
@labour.route("/profile/<int:user_id>/edit", methods=["POST"])
@login_required
def edit_labour_profile(user_id):

    if current_user.id != user_id:
        flash("You can only edit your own profile.", "danger")
        return redirect(url_for("labour.labour_profile", user_id=user_id))

    username = request.form.get("username", "").strip()
    city = request.form.get("city", "").strip()
    phone = request.form.get("phone", "").strip()

    # ✅ VALIDATION
    if not username:
        flash("Username cannot be empty.", "danger")
        return redirect(url_for("labour.labour_profile", user_id=user_id))

    # Optional but safe checks
    if phone and not phone.isdigit():
        flash("Phone number must contain only digits.", "danger")
        return redirect(url_for("labour.labour_profile", user_id=user_id))

    # ✅ UPDATE
    current_user.username = username
    current_user.city = city
    current_user.phone = phone

    db.session.commit()

    logging.info(f"Profile updated: user {current_user.id}")

    flash("Profile updated successfully.", "success")
    return redirect(url_for("labour.labour_profile", user_id=user_id))