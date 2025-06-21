from celery import Celery
from celery.schedules import crontab

import os

CELERY_BROKER_URL = os.getenv('RABBITMQ_URL')
celery_app = Celery(__name__, broker=CELERY_BROKER_URL)

celery_app.conf.update(
    imports=[
        'ai.churnpredict.'  
    ],
    broker_connection_retry_on_startup=True,
    task_track_started=True,
)


celery_app.conf.beat_schedule = {
    'monthly-churn-prediction': {
        'task': 'churn.tasks.run_monthly_churn_prediction',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  
    },
}