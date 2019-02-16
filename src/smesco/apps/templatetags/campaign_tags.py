from django.utils import timezone
from django.conf import settings
from django import template
from oscar.core.loading import get_model
from haystack.query import SearchQuerySet

Banner = get_model('campaign', 'Banner')
BannerMini = get_model('campaign', 'BannerMini')
Endorsement = get_model('campaign', 'Endorsement')

Product = get_model('catalogue', 'Product')

register = template.Library()


@register.simple_tag()
def get_banner_images(limit=False):

    now = timezone.now()
    qs = Banner.objects.filter(published=True, valid_from__lte=now, valid_until__gte=now).order_by('number')

    if limit and qs:
        qs = qs[0:limit]

    return qs


def dummy_banner_mini(queryset):
    dummy = getattr(settings, 'BANNER_MINI_PLACEHOLDER', None)
    limit = getattr(settings, 'MAX_BANNER_MINI', None) | 4
    result = []

    for i in range(limit):
        for d in queryset:
            if d.sort_priority == i:
                result.append(d)
        if dummy and len(result) == i:
            new_dummy = dummy
            new_dummy['sort_priority'] = i
            default_mini_banner = BannerMini(**new_dummy)
            result.append(default_mini_banner)
    return result


@register.simple_tag()
def get_banner_mini():
    queryset = BannerMini.objects.order_by('sort_priority').filter(published=True)
    return dummy_banner_mini(queryset)


@register.simple_tag()
def get_endorsements():
    now = timezone.now()
    queryset = Endorsement.objects.filter(published=True, valid_from__lte=now, valid_until__gte=now)\
        .order_by('sort_priority')
    return queryset


@register.simple_tag()
def get_highlight_products():
    return Product.objects.filter(highlight=True, structure__in=['child', 'standalone'])
