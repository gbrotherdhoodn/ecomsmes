import logging
from utils.middleware.request import NO_REQUEST_ID, SentryLogMiddleware, meta_keys


class QuotelessStr(str):
    """
    Return the repr() of this string *without* quotes.  This is a
    temporary fix until https://github.com/severb/graypy/pull/34 is resolved.
    """
    def __repr__(self):
        return self


class UserFilter(logging.Filter):

    def filter(self, record):
        record.username = ''
        if hasattr(record, 'request'):
            if hasattr(record.request, 'user'):
                record.username = record.request.user.username

        return True


class StaticFieldFilter(logging.Filter):
    """
    Python logging filter that adds the given static contextual information
    in the ``fields`` dictionary to all logging records.
    """

    def __init__(self, name='', fields=None):
        super().__init__(name)
        self.static_fields = fields

    def filter(self, record):
        for k, v in self.static_fields.items():
            setattr(record, k, v)
        return True


class RequestFilter(logging.Filter):
    """
    Python logging filter that removes the (non-pickable) Django ``request``
    object from the logging record.
    """
    def filter(self, record: logging.LogRecord):
        if hasattr(record, 'request'):
            del record.request
        return True


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(SentryLogMiddleware.thread, 'request_id', NO_REQUEST_ID)
        return True


class RequestMetaFilter(logging.Filter):
    def filter(self, record):
        middleware_request = getattr(SentryLogMiddleware.thread, 'request', {})
        if hasattr(middleware_request, 'META'):
            # meta = {key.lower(): str(value) for key, value in record.request.META.items() if key in meta_keys}
            for key, value in middleware_request.META.items():
                if key in meta_keys:
                    setattr(record, key.lower(), str(value))

        return True
