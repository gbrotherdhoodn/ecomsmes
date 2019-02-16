from decimal import Decimal
from django import template
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from oscar.apps.catalogue.models import ProductAttributeValue
from oscar.core.loading import get_model

Benefit = get_model('offer', 'Benefit')
SourceType = get_model('payment', 'SourceType')

register = template.Library()
ri = register.inclusion_tag


@register.simple_tag
def get_scheme():
    scheme = 'http' if settings.DEBUG else 'https'
    return scheme + '://'


@register.inclusion_tag('partials/header.html')
def navigation_component(tree_categories):
    return {
        'tree_categories': tree_categories,
    }


@register.filter(is_safe=True, name='is_new')
def is_new(date_created):
    try:
        return timezone.localtime(timezone.now()) < date_created + \
               timedelta(days=getattr(settings, 'NEW_FLAG_PRODUCT_PERIOD'))
    except Exception:
        return False


@register.simple_tag
def order_flow(status_now, new_status):
    pipeline = getattr(settings, 'OSCAR_ORDER_STATUS_PIPELINE', {})
    available_status = pipeline.get(status_now, {})
    return new_status in available_status


@register.simple_tag
def attribute_detail(product, attribute_type):
    attribute = product.attribute_values.filter(attribute__name=attribute_type).last()
    if not attribute:
        return ''
    if attribute.value_option:
        return attribute.value_option.option
    elif attribute.value_multi_option:
        return attribute.value_as_text


@register.simple_tag
def get_discount_price(offer, price):
    if not price:
        return 0
    total = price
    offer_type = offer.benefit.type
    discount = offer.benefit.value
    price = Decimal(price)
    if offer_type == Benefit.FIXED:
        if discount > price:
            total = 0
        else:
            total = price - discount
    elif offer_type == Benefit.PERCENTAGE:
        total = price - ((price * discount) / 100)
    elif offer_type == Benefit.FIXED_PRICE:
        total = discount

    return total


@register.simple_tag
def get_discount_percent(offer, price):
    if not price:
        return 0
    offer_type = offer.benefit.type
    discount = offer.benefit.value
    price = Decimal(price)
    percent = discount
    if offer_type == Benefit.FIXED:
        if discount > price:
            percent = 100
        else:
            percent = round(((discount / price) * 100), 0)
    elif offer_type == Benefit.FIXED_PRICE:
        percent = round((((price - discount) / price) * 100), 0)

    return int(percent)


@register.simple_tag
def get_total_before_voucher(total, voucher):
    if voucher:
        voucher = list(voucher)[0].get('discount', 0)
    else:
        voucher = 0

    return total + voucher


@register.simple_tag
def delta_time(input_datetime, delta_days):
    return input_datetime + timedelta(days=delta_days)


@register.inclusion_tag('catalogue/partials/variant.html')
def render_variant(product, request, purchase_info_for_product):
    return {
        'product': product,
        'other': product.parent.children.all(),
        'request': request,
        'purchase_info_for_product': purchase_info_for_product
    }


@register.inclusion_tag('checkout/virtual_accounts.html')
def render_virtual_account(source_type):
    payment_list = getattr(settings, 'PAYMENT_LIST')
    payment_step = payment_list.get(source_type.name, None)
    exist_payment_step = []
    bank_name = payment_step.get('name', None)
    atm = payment_step.get('atm', None)
    internet = payment_step.get('internet', None)
    mobile = payment_step.get('mobile', None)
    other = payment_step.get('other', None)
    if atm:
        exist_payment_step.append({'title': f'ATM Bank {bank_name}', 'steps': atm})
    if internet:
        exist_payment_step.append({'title': 'Internet Banking', 'steps': internet})
    if mobile:
        exist_payment_step.append({'title': f'Mobile Banking {bank_name}', 'steps': mobile})
    if other:
        exist_payment_step.append({'title': 'ATM Bank Lain ( Alto, Prima, ATM Bersama )', 'steps': other})

    return {
        'bank_name': source_type.name,
        'payment_steps': exist_payment_step
    }


def _get_variant_descriptors(product):

    descriptors = {}

    for attribute_value in ProductAttributeValue.objects.filter(
                product__in=product.parent.children.all()).select_related('product', 'attribute'):
        attribute_name, value = attribute_value.attribute.name, attribute_value.value
        descriptors.setdefault(attribute_name, {}).setdefault(value, set()).add(attribute_value.product_id)

    return [(attribute, value_map.items()) for attribute, value_map in descriptors.items()]


@register.inclusion_tag('catalogue/partials/variant_descriptors.html')
def render_variant_descriptors(product, query_params):
    return {
        'product': product,
        'query_params': [i[0] for i in query_params.values()] if query_params else [],
        'descriptors': _get_variant_descriptors(product)
    }


@register.inclusion_tag('partials/redirect.html')
def redirect_page(url, query_params):
    from urllib.parse import urlencode
    return {
        'url': f'{url}?{urlencode(query_params)}'
    }


@register.simple_tag
def filtering_wishlist(user_wishlist, product):
    wishlist_with_product = user_wishlist.filter(lines__product=product).last()
    return product if wishlist_with_product else None


@register.simple_tag
def is_buyed(product, user):
    state = False
    if not getattr(user, 'orders', None):
        return state
    orders = user.orders.filter(status=settings.ORDER_STATUS_COMPLETED)

    for order in orders:
        order_lines = order.lines.all().filter(product=product)
        if order_lines:
            state = True
            break

    return state


@register.simple_tag
def acceptance_variant(variants):
    acceptance = {
        'warna': '',
        'ukuran': '',
    }
    for data in variants:
        if data.attribute.code == 'warna':
            acceptance['warna'] = data.value_as_html
        if data.attribute.code == 'ukuran':
            acceptance['ukuran'] = data.value_as_html

    return acceptance

@register.simple_tag
def concate_id(param1, param2):
    return str(param1)+str(param2)

@register.simple_tag
def recommended_products(product):
    if product.is_standalone:
        recommended_product = product.sorted_recommended_products
    else:
        recommended_product = product.parent.sorted_recommended_products

    return recommended_product


@register.simple_tag
def get_unit_price(line):
    if line.is_tax_known:
        unit_price = line.unit_price_incl_tax
    else:
        unit_price = line.unit_price_excl_tax

    return unit_price


@register.simple_tag
def get_subtotal_price(unit_price, quantity):
    return unit_price * quantity


@register.simple_tag
def get_voucher_list(offers):
    voucher = offers.filter(voucher_id__isnull=False).first()
    return voucher


@register.simple_tag
def get_image_bank(source_type):
    images = SourceType.objects.get_queryset().image_by_source_type(source_type=source_type)
    return images


@register.simple_tag
def get_payment_method(source_type):
    payment_method = SourceType.objects.get_queryset().by_source_type(source_type=source_type)
    return payment_method


def gtm_tag(google_tag_id=None):
    if google_tag_id is None:
        google_tag_id = getattr(settings, 'OSCAR_GOOGLE_ANALYTICS_ID', None)
    return {
        'google_tag_id': google_tag_id
    }


@register.simple_tag
def get_count_summary_order(order, key):
    return sum([getattr(o, key) for o in order])


@register.simple_tag
def recommended_product(product):
    if product.is_standalone:
        recommended_product = product.sorted_recommended_products
    else:
        recommended_product = product.parent.sorted_recommended_products

    return recommended_product


ri("partials/gtm/gtm_head.html", name='gtm_head')(gtm_tag)
ri("partials/gtm/gtm_body.html", name='gtm_body')(gtm_tag)
