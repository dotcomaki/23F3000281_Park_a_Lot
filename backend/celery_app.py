# backend/celery_app.py

from celery import Celery
from .app import create_app
from .config import Config

def make_celery(app=None):
    """
    Factory to create a Celery instance tied to our Flask app.
    """
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config.get('CELERY_RESULT_BACKEND', app.config['CELERY_BROKER_URL']),
        include=['backend.tasks']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    return celery

# Instantiate a global Celery
celery = make_celery()