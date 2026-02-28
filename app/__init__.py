from flask import Flask
from config import Config
from app.extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from app.auth.routes import auth
    app.register_blueprint(auth)

    return app