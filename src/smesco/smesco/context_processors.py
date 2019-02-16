from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def print_r(data):
    return {
        "testing": str(dir(data))
    }


def global_settings(request):

    return {
        'debug': getattr(settings, 'DEBUG', None),
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', None),
        # 'PAYMENT_AVAILABLE': getattr(settings, 'PAYMENT_AVAILABLE',
        # 'PAYMENT_LIST': getattr(settings, 'PAYMENT_LIST',
        'SOCIAL_FACEBOOK': getattr(settings, 'SOCIAL_FACEBOOK', None),
        'SOCIAL_INSTAGRAM': getattr(settings, 'SOCIAL_INSTAGRAM', None),
        'SOCIAL_TWITTER': getattr(settings, 'SOCIAL_TWITTER', None),
        'SOCIAL_YOUTUBE': getattr(settings, 'SOCIAL_YOUTUBE', None),
        'SHOP_NAME': getattr(settings, 'OSCAR_SHOP_NAME', None),
    }
