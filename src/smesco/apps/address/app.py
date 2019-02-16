from oscar.core.application import Application
from oscar.core.loading import get_class


class AddressApplication(Application):
    name = 'address'
    list_states = get_class('apps.address.views', 'load_states')

    def get_urls(self):
        urls = []
        return self.post_process_urls(urls)


application = AddressApplication()
