# backend/tasks.py

from .celery_app import celery
from .config import Config
from .extensions import db
from .extensions import mail
from .models import User, Reservation, ParkingSpot
from datetime import datetime, date
from sqlalchemy import func
from flask_mail import Message
import requests

import os
import csv
from io import StringIO
from datetime import datetime

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
    Generate and send monthly report via email.
    """
    # Determine current month range
    today = date.today()
    first_of_month = today.replace(day=1)

    # Count & sum for the month
    total_reservations = (
        Reservation.query
        .filter(
            db.func.date(Reservation.parked_at) >= first_of_month,
            db.func.date(Reservation.parked_at) <= today
        )
        .count()
    )
    total_spent = (
        db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0))
        .filter(
            Reservation.parked_at >= first_of_month,
            Reservation.parked_at <= today,
            Reservation.parking_cost != None
        )
        .scalar()
    )

    # Build email content
    month_name = today.strftime("%B %Y")
    subject = f"Monthly Parking Report — {month_name}"
    body = (
        f"Hi {{username}},\n\n"
        f"Here’s your parking summary for {month_name}:\n"
        f"  • Total Reservations: {total_reservations}\n"
        f"  • Total Spent: ₹{total_spent:.2f}\n\n"
        "Thank you for using our Parking App!"
    )

    # Email each non-admin user
    users = User.query.filter(User.role != 'admin').all()
    for user in users:
        msg = Message(
            subject=subject,
            recipients=[user.email]
        )
        msg.body = body.format(username=user.username)
        try:
            mail.send(msg)
            print(f"[MonthlyReport] Successfully emailed report to {user.email}")
        except Exception as e:
            print(f"[MonthlyReport] Failed to email {user.email}: {e}")


# Task: Generate a CSV of all reservations for a given user and return the file path.
@celery.task(bind=True)
def generate_user_csv(self, user_id):
    """
    Generate a CSV of all reservations for the given user and return the file path.
    CSV Format includes: Reservation ID, Lot Name, Lot ID, Spot ID, 
    Parked At, Left At, Duration (hours), Cost, Status, Remarks
    """
    try:
        # Query reservations for this user with related data
        resvs = (Reservation.query
                .filter_by(user_id=user_id)
                .join(Reservation.spot)
                .join(ParkingSpot.lot)
                .order_by(Reservation.parked_at.desc())
                .all())

        # Prepare CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Enhanced header row with more details
        writer.writerow([
            'Reservation ID', 'Lot Name', 'Lot ID', 'Spot ID',
            'Parked At', 'Left At', 'Duration (Hours)', 'Cost (₹)', 
            'Status', 'Remarks', 'Export Date'
        ])
        
        # Data rows with enhanced information
        for r in resvs:
            # Calculate duration if reservation is completed
            duration = ''
            status = 'Active' if not r.left_at else 'Completed'
            
            if r.left_at and r.parked_at:
                duration_delta = r.left_at - r.parked_at
                duration = f"{duration_delta.total_seconds() / 3600:.2f}"
            
            # Format timestamps for better readability
            parked_at_str = r.parked_at.strftime('%Y-%m-%d %H:%M:%S') if r.parked_at else ''
            left_at_str = r.left_at.strftime('%Y-%m-%d %H:%M:%S') if r.left_at else ''
            
            writer.writerow([
                r.id,
                r.spot.lot.prime_location_name,  # Lot name
                r.spot.lot_id,
                r.spot_id,
                parked_at_str,
                left_at_str,
                duration,
                f"{r.parking_cost:.2f}" if r.parking_cost else '0.00',
                status,
                r.remarks or '',
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Export timestamp
            ])

        # Save to file
        exports_dir = os.path.join(os.getcwd(), 'backend', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"user_{user_id}_parking_history_{timestamp}.csv"
        file_path = os.path.join(exports_dir, filename)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())

        print(f"[CSV Export] Successfully generated CSV for user {user_id}: {filename}")
        return file_path
        
    except Exception as e:
        print(f"[CSV Export] Error generating CSV for user {user_id}: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)
