import logging
import threading
import uuid

from django.conf import settings
from django.core.signals import request_finished

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

local = threading.local()

REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
LOG_REQUESTS_SETTING = 'LOG_REQUESTS'
NO_REQUEST_ID = "none"  # Used if no request ID is available
REQUEST_ID_RESPONSE_HEADER_SETTING = 'REQUEST_ID_RESPONSE_HEADER'
OUTGOING_REQUEST_ID_HEADER_SETTING = 'OUTGOING_REQUEST_ID_HEADER'
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING = 'GENERATE_REQUEST_ID_IF_NOT_IN_HEADER'

logger = logging.getLogger(__name__)

meta_keys = ['PATH_INFO', 'HTTP_X_SCHEME', 'REMOTE_ADDR',
             'TZ', 'REMOTE_HOST', 'CONTENT_TYPE', 'CONTENT_LENGTH', 'HTTP_AUTHORIZATION',
             'HTTP_HOST', 'HTTP_USER_AGENT', 'HTTP_X_USER_AGENT', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP',
             'HTTP_X_REQUEST_ID']


class SentryMiddleware(MiddlewareMixin):
    thread = threading.local()

    def _get_request_id(self, request):
        request_id_header = getattr(settings, REQUEST_ID_HEADER_SETTING, None)
        generate_request_if_not_in_header = getattr(settings, GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING, False)

        if request_id_header:
            # fallback to NO_REQUEST_ID if settings asked to use the
            # header request_id but none provided
            default_request_id = NO_REQUEST_ID

            # unless the setting GENERATE_REQUEST_ID_IF_NOT_IN_HEADER
            # was set, in which case generate an id as normal if it wasn't
            # passed in via the header
            if generate_request_if_not_in_header:
                default_request_id = self._generate_id()

            return request.META.get(request_id_header, default_request_id)

        return self._generate_id()

    def _generate_id(self):
        return uuid.uuid4().hex

    def process_request(self, request):
        request_id = self._get_request_id(request)
        SentryMiddleware.thread.request = request
        SentryMiddleware.thread.request_id = request_id
        # we utilize request_finished as the exception gets reported
        # *after* process_response is executed, and thus clearing the
        # transaction there would leave it empty
        # XXX(dcramer): weakref's cause a threading issue in certain
        # versions of Django (e.g. 1.6). While they'd be ideal, we're under
        # the assumption that Django will always call our function except
        # in the situation of a process or thread dying.
        request_finished.connect(self.request_finished, weak=False)

    def request_finished(self, **kwargs):

        SentryMiddleware.thread.request = None
        SentryMiddleware.thread.request_id = None

        request_finished.disconnect(self.request_finished)


SentryLogMiddleware = SentryMiddleware

