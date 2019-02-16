import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def get_mailchimp_client():
    from .mailchimp import MailChimpClient
    return MailChimpClient(settings.MAILCHIMP_API_KEY,
                           settings.MAILCHIMP_SUBSCRIBE_LIST_ID)


def get_kgx_client():
    from .kgx import KgxClient
    return KgxClient(settings.KGX_API_URL,
                     settings.KGX_API_USERNAME,
                     settings.KGX_API_PASSWORD,
                     settings.KGX_ORIGIN_ZIP_CODE)
