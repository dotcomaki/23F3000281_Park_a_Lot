import os
from pathlib import Path

# Base directory to locate your SQLite file
BASEDIR = Path(__file__).parent.resolve()

class Config:
    # Flask secret key (override via env if you like)
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-will-never-guess")

    # SQLAlchemy / SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASEDIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Use local Redis for Celery broker and results by default
    CELERY_BROKER_URL = os.environ.get(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1"
    )

   # URL for Google Chat incoming webhook
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL",
       "https://chat.googleapis.com/v1/spaces/AAQAVvLThTU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=X1BBEf2iwPEJmSqOrBi8lSybsbPHZl6dxHGvXDGE38E"
    )

    # Flask-Caching configuration
    # Type of cache to use (e.g., 'redis' or 'simple')
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")
    # Redis server URL for caching (defaults to Celery broker Redis)
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/0")
    # Default timeout (in seconds) for cached values
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 60))

    # Flask-Mail configuration
    MAIL_SERVER        = os.getenv("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT          = int(os.getenv("MAIL_PORT",  "587"))
    MAIL_USE_TLS       = os.getenv("MAIL_USE_TLS",  "true").lower() in ("true","1","yes")
    MAIL_USERNAME      = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD      = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER= os.getenv("MAIL_DEFAULT_SENDER")