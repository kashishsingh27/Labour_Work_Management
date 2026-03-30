from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, Notification, Rating, User
from flask_mail import Message
from app.extensions import mail
from sqlalchemy import func
from datetime import datetime


contractor = Blueprint("contractor", __name__, url_prefix="/contractor")


@contractor.route("/dashboard")
@login_required
def contractor_dashboard():
    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    # Stats
    jobs_posted           = Job.query.filter_by(contractor_id=current_user.id).count()
    applications_received = Application.query.join(Job).filter(Job.contractor_id == current_user.id).count()
    ratings_given         = Rating.query.filter_by(contractor_id=current_user.id).count()
    pending_count         = Application.query.join(Job).filter(
                                Job.contractor_id == current_user.id,
                                Application.status == "Pending"
                            ).count()

    # Recent jobs posted (last 5)
    recent_jobs = Job.query.filter_by(contractor_id=current_user.id)\
                    .order_by(Job.created_at.desc()).limit(4).all()

    # Pending applications needing action (last 6)
    pending_applications = Application.query.join(Job).filter(
                                Job.contractor_id == current_user.id,
                                Application.status == "Pending"
                            ).order_by(Application.id.desc()).limit(6).all()

    jobs_by_applicants = db.session.query(
                                Job, func.count(Application.id).label("app_count")
                            ).join(Application, Application.job_id == Job.id)\
                            .filter(Job.contractor_id == current_user.id)\
                            .group_by(Job.id)\
                            .order_by(func.count(Application.id).desc())\
                            .limit(5).all()

    # Recent ratings given (last 4)
    recent_ratings = Rating.query.filter_by(contractor_id=current_user.id)\
                        .order_by(Rating.created_at.desc()).limit(4).all()

    return render_template(
        "contractor/dashboard.html",
        jobs_posted           = jobs_posted,
        applications_received = applications_received,
        ratings_given         = ratings_given,
        pending_count         = pending_count,
        recent_jobs           = recent_jobs,
        pending_applications  = pending_applications,
        jobs_by_applicants    = jobs_by_applicants,
        recent_ratings        = recent_ratings,
    )


@contractor.route("/post-job", methods=["GET", "POST"])
@login_required
def post_job():

    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        city = request.form.get("city")
        locality = request.form.get("locality")
        landmark = request.form.get("landmark")
        pincode = request.form.get("pincode")
        wage = request.form.get("wage")
        work_type = request.form.get("work_type")

        job = Job(
            title=title,
            description=description,
            city=city,
            locality=locality,
            landmark=landmark,
            pincode=pincode,
            wage=wage,
            work_type=work_type,
            contractor=current_user
        )

        db.session.add(job)
        db.session.commit()

        # notify labours
        labours = User.query.filter_by(role="labour", city=city).all()

        for labour in labours:

            notification = Notification(
                user_id=labour.id,
                message=f"New job posted in {city}: {title}",
                job_id=job.id
            )

            db.session.add(notification)

            msg = Message(
                subject="New Job Available in Your City",
                recipients=[labour.email]
            )

            msg.body = f"""
Hello {labour.username},

A new job has been posted in {city}.

Job Title: {title}
Wage: ₹{wage}

Login to the system to apply.

LWMS Team
"""

            mail.send(msg)

        db.session.commit()

        flash("Job posted successfully!", "success")
        return redirect(url_for("contractor.contractor_dashboard"))

    return render_template("contractor/post_job.html")


@contractor.route("/applications")
@login_required
def view_applications():
    if current_user.role != "contractor":
        flash("Access denied.")
        return redirect(url_for("auth.login"))

    jobs = Job.query.filter_by(contractor_id=current_user.id).all()

    applications = []
    for job in jobs:
        for app in job.applications:
            applications.append(app)

    applications.sort(
        key=lambda a: a.created_at if a.created_at else datetime.min,
        reverse=True
    )

    return render_template(
        "contractor/applications.html",
        applications=applications
    )


@contractor.route("/application/<int:app_id>/accept")
@login_required
def accept_application(app_id):

    application = Application.query.get_or_404(app_id)

    if current_user.id != application.job.contractor_id:
        flash("Unauthorized action.")
        return redirect(url_for("contractor.contractor_dashboard"))

    application.status = "Accepted"
    notification = Notification(
        user_id=application.labour_id,
        message=f"Your application for '{application.job.title}' was accepted.",
        job_id=application.job_id
        )
    db.session.add(notification)
    db.session.commit()

    msg = Message(
    subject="Job Application Accepted - LWMS",
    recipients=[application.labour.email]
   )

    msg.body = f"""
    Hello {application.labour.username},

    Congratulations! Your application for the job has been accepted.

    Job Details
    -----------------------
    Title: {application.job.title}
    City: {application.job.city}
    Wage: ₹{application.job.wage}

    Contractor Details
    -----------------------
    Name: {current_user.username}
    Phone: {current_user.phone}

    Please contact the contractor to start the work.

    Regards,
    Labour Work Management System(LWMS)
    """

    mail.send(msg)

    flash("Application accepted.")
    return redirect(url_for("contractor.view_applications"))


@contractor.route("/application/<int:app_id>/reject")
@login_required
def reject_application(app_id):

    application = Application.query.get_or_404(app_id)

    if current_user.id != application.job.contractor_id:
        flash("Unauthorized action.")
        return redirect(url_for("contractor.contractor_dashboard"))

    application.status = "Rejected"
    notification = Notification(
        user_id=application.labour_id,
        message=f"Your application for '{application.job.title}' was rejected.",
        job_id=application.job_id
    )

    db.session.add(notification)
    db.session.commit()

    flash("Application rejected.")
    return redirect(url_for("contractor.view_applications"))


@contractor.route("/rate/<int:job_id>/<int:labour_id>", methods=["GET","POST"])
@login_required
def rate_labour(job_id, labour_id):

    if current_user.role != "contractor":
        return redirect(url_for("auth.login"))

    existing_rating = Rating.query.filter_by(
        job_id=job_id,
        labour_id=labour_id,
        contractor_id=current_user.id
    ).first()

    if existing_rating:
        flash("You already rated this worker.", "warning")
        return redirect(url_for("contractor.view_applications", job_id=job_id))

    if request.method == "POST":

        rating_value = request.form.get("rating")
        review = request.form.get("review")

        rating = Rating(
            job_id=job_id,
            labour_id=labour_id,
            contractor_id=current_user.id,
            rating=rating_value,
            review=review
        )

        db.session.add(rating)
        db.session.commit()

        flash("Worker rated successfully!", "success")

        return redirect(url_for("contractor.contractor_dashboard"))

    return render_template(
        "contractor/rate_labour.html",
        job_id=job_id,
        labour_id=labour_id
    )

@contractor.route("/profile/<int:user_id>")
@login_required
def contractor_profile(user_id):
    contractor = User.query.get_or_404(user_id)
    if contractor.role != "contractor":
        flash("User is not a contractor.", "danger")
        return redirect(url_for("auth.home"))

    jobs_list             = Job.query.filter_by(contractor_id=user_id).order_by(Job.created_at.desc()).all()
    job_ids               = [job.id for job in jobs_list]
    applications_received = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    hires_made            = Application.query.filter(Application.job_id.in_(job_ids), Application.status == "Accepted").count() if job_ids else 0
    pending_apps          = Application.query.filter(Application.job_id.in_(job_ids), Application.status == "Pending").count() if job_ids else 0
    workers_rated         = Rating.query.filter_by(contractor_id=user_id).count()
    ratings_list          = Rating.query.filter_by(contractor_id=user_id).order_by(Rating.created_at.desc()).all()

    return render_template("contractor/contractor_profile.html",
        contractor=contractor,
        jobs_list=jobs_list,
        applications_received=applications_received,
        hires_made=hires_made,
        pending_apps=pending_apps,
        workers_rated=workers_rated,
        ratings_list=ratings_list,
    )

@contractor.route("/profile/<int:user_id>/edit", methods=["POST"])
@login_required
def edit_contractor_profile(user_id):
    if current_user.id != user_id:
        flash("You can only edit your own profile.", "danger")
        return redirect(url_for("contractor.contractor_profile", user_id=user_id))
    
    current_user.username = request.form.get("username", current_user.username).strip()
    current_user.city = request.form.get("city", current_user.city or "").strip()
    current_user.phone = request.form.get("phone", current_user.phone or "").strip()
    
    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("contractor.contractor_profile", user_id=user_id))

@contractor.route("/job/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.id != job.contractor_id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("contractor.view_applications"))
    # Delete related records first
    Application.query.filter_by(job_id=job.id).delete()
    Notification.query.filter_by(job_id=job.id).delete()
    Rating.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully.", "success")
    return redirect(url_for("contractor.view_applications"))
