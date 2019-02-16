from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def multiply(qty, price):
    return qty * price


@register.filter()
def to_range(value):
    return range(int(value))


@register.filter()
def no_star(value):
    return range(5 - int(value))


@register.filter()
def split_url(value):
    return value.split('/')[1]


@register.filter()
def get_value_payment(data, key_name):
    return data[key_name]


@register.filter()
def query_transform(request):
    return request.GET.get('sort-by')


@register.filter()
def odd(num):
    return num % 2 == 0


@register.filter()
def active_url(value):
    return value.split('/')[2]


@register.simple_tag
def media_url():
    return settings.MEDIA_URL


@register.simple_tag
def query_transform(request):
    text = request
    head, sep, tail = text.partition('&sort_by=')
    return head


@register.simple_tag
def get_category(data):
    val = data.values()
    if val:
        return val[0]['name']
    else:
        return '-'


@register.simple_tag
def total_before_voucher(total, voucher):
    if voucher:
        return total + voucher.amount
    else:
        return total
