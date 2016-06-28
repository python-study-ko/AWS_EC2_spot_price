from celery import Celery
from tasks import celery_settings

celeryapp = Celery('tasks', include=['tasks.tasks'])
celeryapp.config_from_object(celery_settings)
