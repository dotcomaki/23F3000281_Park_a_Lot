import os
from pathlib import Path

BASEDIR = Path(__file__).parent.resolve()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-will-never-guess")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASEDIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.environ.get(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1"
    )

    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL",
       "https://chat.googleapis.com/v1/spaces/AAQAVvLThTU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=X1BBEf2iwPEJmSqOrBi8lSybsbPHZl6dxHGvXDGE38E"
    )

    CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 60))

    MAIL_SERVER        = os.getenv("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT          = int(os.getenv("MAIL_PORT",  "587"))
    MAIL_USE_TLS       = os.getenv("MAIL_USE_TLS",  "true").lower() in ("true","1","yes")
    MAIL_USERNAME      = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD      = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("Parking App", "akifmoimpct@gmail.com")