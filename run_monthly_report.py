from backend.app import create_app
from backend.celery_app import celery

app = create_app()
with app.app_context():
    result = celery.send_task('backend.tasks.send_monthly_report')
    print("Task sent, ID:", result.id)