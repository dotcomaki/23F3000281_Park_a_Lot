# backend/tasks.py

from celery import Celery
from celery.schedules import crontab
from .config import Config
from .extensions import db
from .models import User, Reservation
from datetime import datetime
from flask_mail import Message, Mail

# Initialize Celery
celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)
celery.conf.update(
    result_expires=3600,
    timezone="Asia/Kolkata",
    beat_schedule={
        # Daily reminder at 18:00 Asia/Kolkata
        'daily-reminder': {
            'task': 'backend.tasks.send_daily_reminder',
            'schedule': crontab(hour=18, minute=0),
        },
        # Monthly activity report on the 1st at 00:05
        'monthly-report': {
            'task': 'backend.tasks.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=5),
        },
    }
)

# Set up Flask-Mail (Mail instance should be init_app in your create_app)
mail = Mail()

@celery.task
def ping():
    """Simple test task."""
    return 'pong'

@celery.task
def send_daily_reminder():
    """
    Send daily reminder to users who haven't reserved today.
    """
    # We need application context to query and send mail
    from backend.app import create_app
    app = create_app()
    mail.init_app(app)
    with app.app_context():
        today = datetime.utcnow().date()
        users = User.query.all()
        for user in users:
            # skip admin
            if user.role == 'admin':
                continue
            # check if user has a reservation today
            has_today = Reservation.query.filter(
                Reservation.user_id == user.id,
                db.func.date(Reservation.parked_at) == today
            ).first()
            if not has_today:
                msg = Message(
                    'Daily Parking Reminder',
                    recipients=[user.email]
                )
                msg.body = (
                    "You haven't booked a parking spot today. "
                    "Log in to reserve if needed."
                )
                mail.send(msg)

@celery.task
def send_monthly_report():
    """
    Generate and email monthly activity report to users.
    """
    from backend.app import create_app
    app = create_app()
    mail.init_app(app)
    with app.app_context():
        # Implement report generation here
        # For each non-admin user, compile stats and send email
        pass
