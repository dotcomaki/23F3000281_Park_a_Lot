from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

# initialize extensions (no app bound yet)
db = SQLAlchemy()
login = LoginManager()

def create_app():
    """Application factory; returns a Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions with this app
    db.init_app(app)
    login.init_app(app)
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id):
        # lazy‐import to avoid circular imports
        from .models import User
        return User.query.get(int(user_id))

    from . import models

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from .routes.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    return app