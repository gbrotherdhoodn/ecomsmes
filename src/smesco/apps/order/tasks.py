import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from celery import task

from oscar.core.loading import get_model, get_class


OrderNote = get_model('order', 'OrderNote')
Order = get_model('order', 'Order')

EventHandler = get_class('order.processing', 'EventHandler')

logger = logging.getLogger('smesco')


@task(name='auto_update_order_status')
def auto_update_order_status():
    statuses = [
        {'old_status': settings.ORDER_STATUS_PLACED,
         'new_status': settings.ORDER_STATUS_CANCELED,
         'day': settings.DEFAULT_DAYS_AUTO_CANCELED
         },
        {'old_status': settings.ORDER_STATUS_SHIPPED,
         'new_status': settings.ORDER_STATUS_COMPLETED,
         'day': settings.DEFAULT_DAYS_AUTO_COMPLETE
         }
    ]

    for status in statuses:
        change_date = timezone.localtime(timezone.now()).date() - timedelta(days=status['day'])
        query = OrderNote.objects.filter(new_status=status['old_status'],
                                         order__status=status['old_status'],
                                         date_created__lte=change_date)
        logger.info(f"executing change status with order {query}")
        for ordernote in query:
            order = ordernote.order
            handler = EventHandler(order.user)
            handler.handle_order_status_change(order, status['new_status'])
            logger.info(f"executing change status success order {order}")

