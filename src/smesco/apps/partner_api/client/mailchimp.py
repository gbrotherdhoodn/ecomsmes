import mailchimp
from ..decorators import run_async


class MailChimpClient(object):
    """Mail Chimp Client"""
    def __init__(self, api_key, list_id):
        self.api_key = api_key
        self.list_id = list_id
        self.api_service = mailchimp.Mailchimp(self.api_key)

    def call_service(self):
        return mailchimp.Mailchimp(self.api_key)

    @run_async
    def subscribe_email_list(self, email):
        try:
            result, response = True, self.call_service().lists.subscribe(self.list_id, {'email': email})
        except Exception as e:
            result, response = False, str(e)
        return result, response

