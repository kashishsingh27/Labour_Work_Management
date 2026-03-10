import os

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = "devikhushi466@gmail.com"
    MAIL_PASSWORD = "iufbtipklevgzdok"

    MAIL_DEFAULT_SENDER = "devikhushi466@gmail.com"