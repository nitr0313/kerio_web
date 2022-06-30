import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'checking_outdated_unpaid_orders': {
        'task': 'cart.tasks.send_view_count_report',
        'schedule': crontab(minute=0, hour=0),  # в полночь
    },
    'send_notify_about_outdated_unpaid_orders': {
        'task': 'cart.tasks.notify_customer_outdated_unpaid_orders',
        'schedule': crontab(hour='*/3'),  # каждые 3 часа
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
