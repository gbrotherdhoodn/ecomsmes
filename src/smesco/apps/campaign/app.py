from django.urls import path
from oscar.core.application import Application
from .views import subscribe


class CampaignApplication(Application):
    name = 'campaign'

    def get_urls(self):
        urls = [
            path('subscribe/', subscribe, name='subscribe'),
        ]
        return self.post_process_urls(urls)


application = CampaignApplication()
