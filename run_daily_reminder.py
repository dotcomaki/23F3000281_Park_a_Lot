from backend.app import create_app
from backend.celery_app import celery

app = create_app()
with app.app_context():
    result = celery.send_task('backend.tasks.send_daily_reminder')
    print("Daily reminder task sent, ID:", result.id)
    print("Google Chat reminders will be sent to users who haven't parked today.")
