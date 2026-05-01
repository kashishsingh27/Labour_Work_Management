from flask import Flask
from config import Config
from app.extensions import db, login_manager, bcrypt, mail, migrate
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging (Render-friendly)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    # Register blueprints
    from app.auth.routes import auth
    from app.contractor.routes import contractor
    from app.labour.routes import labour

    app.register_blueprint(auth)
    app.register_blueprint(contractor)
    app.register_blueprint(labour)

    return app