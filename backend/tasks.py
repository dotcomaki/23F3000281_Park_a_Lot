# backend/tasks.py

from .celery_app import celery
from .config import Config
from .extensions import db
from .models import User, Reservation
from datetime import datetime, date
import requests

@celery.task
def ping():
    """Simple test task."""
    return 'pong'

@celery.task
def send_daily_reminder():
    """
    Send daily reminder to users who haven't reserved today.
    """
    webhook = Config.GOOGLE_CHAT_WEBHOOK_URL
    today = date.today()
    # Collect IDs of users who reserved today
    done_ids = {
        r.user_id
        for r in Reservation.query.filter(
            db.func.date(Reservation.parked_at) == today
        ).all()
    }
    # Notify each non-admin user who hasn't reserved today
    for user in User.query.filter(User.role != 'admin'):
        if user.id in done_ids:
            continue
        text = (
            f"Hi {user.username}! You haven’t parked today. "
            "If you need a spot, please book one now: https://your-app-url/"
        )
        payload = { "text": text }
        try:
            requests.post(webhook, json=payload, timeout=5)
        except Exception as e:
            print(f"Failed to send chat reminder to {user.username}: {e}")

@celery.task
def send_monthly_report():
    """
    Generate and send monthly report via Google Chat or other channel.
    """
    # TODO: implement monthly report logic
    pass
