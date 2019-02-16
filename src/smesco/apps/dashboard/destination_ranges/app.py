from django.conf.urls import url

from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class DestinationRangeDashboardApplication(DashboardApplication):
    name = None
    default_permissions = ['is_staff', ]

    list_view = get_class('apps.dashboard.destination_ranges.views', 'RangeListView')
    create_view = get_class('apps.dashboard.destination_ranges.views', 'RangeCreateView')
    update_view = get_class('apps.dashboard.destination_ranges.views', 'RangeUpdateView')
    delete_view = get_class('apps.dashboard.destination_ranges.views', 'RangeDeleteView')

    def get_urls(self):
        urlpatterns = [
            url(r'^$', self.list_view.as_view(), name='destination-range-list'),
            url(r'^create/$', self.create_view.as_view(), name='destination-range-create'),
            url(r'^(?P<pk>\d+)/$', self.update_view.as_view(), name='destination-range-update'),
            url(r'^(?P<pk>\d+)/delete/$', self.delete_view.as_view(), name='destination-range-delete'),
        ]
        return self.post_process_urls(urlpatterns)


application = DestinationRangeDashboardApplication()
