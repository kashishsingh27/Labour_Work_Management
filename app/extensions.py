from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate

# Extension instances created here without an app — bound to the app in create_app() via init_app()
mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

# Redirect to login if a protected route is accessed without authentication
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"