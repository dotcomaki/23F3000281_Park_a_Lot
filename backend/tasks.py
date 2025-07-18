# backend/tasks.py

from .celery_app import celery
from .config import Config
from .extensions import db
from .models import User, Reservation
from datetime import datetime, date
from sqlalchemy import func
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
    Generate and send monthly report via Google Chat webhook.
    """
    # Determine current month range
    today = date.today()
    first_of_month = today.replace(day=1)

    # Count total reservations in current month
    total_reservations = (
        Reservation.query
        .filter(
            db.func.date(Reservation.parked_at) >= first_of_month,
            db.func.date(Reservation.parked_at) <= today
        )
        .count()
    )

    # Sum total parking_cost in current month
    total_spent = (
        db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0))
        .filter(
            Reservation.parked_at >= first_of_month,
            Reservation.parked_at <= today,
            Reservation.parking_cost != None
        )
        .scalar()
    )

    # Build message
    month_name = today.strftime("%B %Y")
    text = (
        f"*Monthly Parking Report — {month_name}*\n"
        f"• Total Reservations: {total_reservations}\n"
        f"• Total Revenue: ₹{total_spent:.2f}"
    )
    payload = {"text": text}
    # Send to Google Chat webhook
    try:
        requests.post(Config.GOOGLE_CHAT_WEBHOOK_URL, json=payload, timeout=10).raise_for_status()
    except Exception as e:
        print(f"[MonthlyReport] Failed to send report: {e}")
