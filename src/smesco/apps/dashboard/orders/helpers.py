import datetime
from apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue
from apps.order.models import ShippingEvent, ShippingEventType, ShippingEventQuantity
from apps.partner_api.client import get_kgx_client


def get_total_weight(basket_products):
    weight = 0
    for basket_product in basket_products:
        product = Product.objects.get(id=basket_product.product_id)
        if product.parent_id:
            product = Product.objects.get(id=product.parent_id)

        attribute_id = ProductAttribute.objects.get(product_class_id=product.product_class_id, code='berat')
        product_attribute = ProductAttributeValue.objects.get(product_id=basket_product.product_id,
                                                              attribute_id=attribute_id)

        if attribute_id.type == 'float':
            weight += product_attribute.value_float * basket_product.quantity
        elif attribute_id.type == 'integer':
            weight += product_attribute.value_integer * basket_product.quantity

    return weight


def add_shipping_event(_shipping_events, event_type_name, order, notes=''):
    event_type, __ = ShippingEventType.objects.get_or_create(name=event_type_name)

    if _shipping_events is None:
        _shipping_events = []
    event = ShippingEvent(event_type=event_type, order=order, notes=notes)
    event.save()
    for line in order.lines.all():
        ShippingEventQuantity.objects.create(event=event, line=line, quantity=line.quantity)


def get_history_shipping(order):
    if order.shipping_events.all() and order.shipping_code == 'kgx-courier':
        order_id = order.number
        awb = order.shipping_events.first().notes
        kgx_client = get_kgx_client()
        shipping_history = kgx_client.get_order_history(order_id)
        line_quantities = order.shipping_events.first().line_quantities
        history_result = []
        for history in shipping_history['data']:
            date_str = history['timestamp']
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            date_created = datetime.datetime.strftime(date_obj, '%d %b. %Y, %H.%M')
            tmp_value = {
                "date_created": date_created,
                "event_type": {
                    "name": history['order_status']
                },
                "notes": awb,
                "driver_name": history['driver_name'] if 'driver_name' in history else "-",
                "driver_phone": history['driver_phone_number'] if 'driver_phone_number' in history else "-",
                "line_quantities": line_quantities
            }
            history_result.append(tmp_value)

            if 'failed_attempts' in history:
                for failure in history['failed_attempts']:
                    date_tmp_str = failure['attempt_time']
                    date_tmp_obj = datetime.datetime.strptime(date_tmp_str, '%Y-%m-%d %H:%M:%S')
                    date_tmp_created = datetime.datetime.strftime(date_tmp_obj, '%d %b. %Y, %H.%M')
                    tmp_val = {
                        "date_created": date_tmp_created,
                        "event_type": {
                            "name": failure['reason']
                        },
                        "notes": awb,
                        "driver_name": history['driver_name'] if 'driver_name' in history else "-",
                        "driver_phone": history['driver_phone_number'] if 'driver_phone_number' in history else "-",
                        "line_quantities": line_quantities
                    }
                    history_result.append(tmp_val)

        return history_result
    else:
        return order.shipping_events.all()
