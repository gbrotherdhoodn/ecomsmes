from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'auto_update_order_status': {
        'task': 'auto_update_order_status',
        'schedule': crontab(minute='*/30'),
    },
}
