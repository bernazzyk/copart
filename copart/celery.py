from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'copart.settings')

app = Celery('copart', broker='redis://redis')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_BROKER_URL='redis://redis',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='America/Regina',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE={
        # 'say_hello': {
        #     'task': 'product.tasks.say_hello',
        #     'schedule': crontab(minute='*/1'),
        #     'args': ()
        # },
        # 'say_ok': {
        #     'task': 'product.tasks.say_ok',
        #     'schedule': crontab(minute='*/1'),
        #     'args': ()
        # },
        # 'scrap_auctions': {
        #     'task': 'product.tasks.scrap_live_auctions',
        #     'schedule': crontab(minute='*/2', hour='15-23,1-2', day_of_week='mon,tue,wed,thu,fri'),
        #     'args': ()
        # },
        # 'scrap_copart_lots': {
        #     'task': 'product.tasks.scrap_copart_lots',
        #     'schedule': crontab(minute=0, hour=3),
        #     'args': ()
        # },
    }
)
