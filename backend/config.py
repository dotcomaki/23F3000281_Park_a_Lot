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

    # Celery / Redis (we’ll wire up Redis later)
    CELERY_BROKER_URL     = os.environ.get(
        "CELERY_BROKER_URL",
        "redis://default:fkivQ9kWg3Xnh9RDe9A6lbtBLnjlCk5Y@redis-17629.crce179.ap-south-1-1.ec2.redns.redis-cloud.com:17629/0"
    )
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND",
        "redis://default:fkivQ9kWg3Xnh9RDe9A6lbtBLnjlCk5Y@redis-17629.crce179.ap-south-1-1.ec2.redns.redis-cloud.com:17629/1"
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