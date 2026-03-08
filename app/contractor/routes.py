from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, Notification, Rating, User


contractor = Blueprint("contractor", __name__, url_prefix="/contractor")


@contractor.route("/dashboard")
@login_required
def contractor_dashboard():

    if current_user.role != "contractor":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    jobs_posted = Job.query.filter_by(contractor_id=current_user.id).count()

    applications_received = Application.query.join(Job).filter(
        Job.contractor_id == current_user.id
    ).count()

    ratings_given = Rating.query.filter_by(contractor_id=current_user.id).count()

    return render_template(
        "contractor/dashboard.html",
        jobs_posted=jobs_posted,
        applications_received=applications_received,
        ratings_given=ratings_given
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

        # notify labours
        labours = User.query.filter_by(role="labour", city=city).all()

        for labour in labours:
            notification = Notification(
                user_id=labour.id,
                message=f"New job posted in {city}: {title}",
                job_id=job.id
            )
            db.session.add(notification)

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
    db.session.commit()

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
    db.session.commit()

    flash("Application rejected.")
    return redirect(url_for("contractor.view_applications"))


@contractor.route("/rate/<int:job_id>/<int:labour_id>", methods=["GET", "POST"])
@login_required
def rate_labour(job_id, labour_id):

    if current_user.role != "contractor":
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        rating_value = int(request.form.get("rating"))
        review = request.form.get("review")

        rating = Rating(
            labour_id=labour_id,
            contractor_id=current_user.id,
            job_id=job_id,
            rating=rating_value,
            review=review
        )

        db.session.add(rating)
        db.session.commit()

        flash("Labour rated successfully!", "success")
        return redirect(url_for("contractor.contractor_dashboard"))

    return render_template("contractor/rate_labour.html")