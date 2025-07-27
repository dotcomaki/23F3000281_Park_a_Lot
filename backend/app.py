from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, cache, mail

def create_app():
    """Application factory; returns a Flask app instance."""
    app = Flask(__name__)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:8080"}})
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    mail.init_app(app)
    jwt = JWTManager(app)

    from . import models

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from .routes.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)