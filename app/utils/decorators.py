from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required


def contractor_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != "contractor":
            flash("Access denied: Contractors only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


def labour_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != "labour":
            flash("Access denied: Labour only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper