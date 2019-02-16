from django.conf.urls import url

from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class CampaignDashboardConfig(DashboardApplication):
    name = None
    default_permissions = ['is_staff', ]

    banner_list_view = get_class('dashboard.campaign.views', 'BannerListView')
    banner_create_view = get_class('dashboard.campaign.views', 'BannerCreateView')
    banner_update_view = get_class('dashboard.campaign.views', 'BannerUpdateView')
    banner_delete_view = get_class('dashboard.campaign.views', 'BannerDeleteView')
    banner_detail_view = get_class('dashboard.campaign.views', 'BannerDetailView')

    banner_mini_list_view = get_class('dashboard.campaign.views', 'BannerMiniListView')
    banner_mini_create_view = get_class('dashboard.campaign.views', 'BannerMiniCreateView')
    banner_mini_update_view = get_class('dashboard.campaign.views', 'BannerMiniUpdateView')
    banner_mini_delete_view = get_class('dashboard.campaign.views', 'BannerMiniDeleteView')
    banner_mini_detail_view = get_class('dashboard.campaign.views', 'BannerMiniDetailView')

    endorsement_list_view = get_class('dashboard.campaign.views', 'EndorsementListView')
    endorsement_create_view = get_class('dashboard.campaign.views', 'EndorsementCreateView')
    endorsement_update_view = get_class('dashboard.campaign.views', 'EndorsementUpdateView')
    endorsement_delete_view = get_class('dashboard.campaign.views', 'EndorsementDeleteView')
    endorsement_detail_view = get_class('dashboard.campaign.views', 'EndorsementDetailView')

    def get_urls(self):
        urls = [
            url(r'^banner/$', self.banner_list_view.as_view(), name='banner-list'),
            url(r'^create-banner/$', self.banner_create_view.as_view(), name='banner-create'),
            url(r'^delete-banner/(?P<pk>\d+)/$', self.banner_delete_view.as_view(), name='banner-delete'),
            url(r'^update-banner/(?P<pk>\d+)/$', self.banner_update_view.as_view(), name='banner-update'),
            url(r'^view-banner/(?P<pk>\d+)/$', self.banner_detail_view.as_view(), name='banner-detail'),

            url(r'^banner-mini/$', self.banner_mini_list_view.as_view(), name='banner-mini-list'),
            url(r'^create-banner-mini/$', self.banner_mini_create_view.as_view(), name='banner-mini-create'),
            url(r'^delete-banner-mini/(?P<pk>\d+)/$', self.banner_mini_delete_view.as_view(), name='banner-mini-delete'),
            url(r'^update-banner-mini/(?P<pk>\d+)/$', self.banner_mini_update_view.as_view(), name='banner-mini-update'),
            url(r'^view-banner-mini/(?P<pk>\d+)/$', self.banner_mini_detail_view.as_view(), name='banner-mini-detail'),

            url(r'^endorsement/$', self.endorsement_list_view.as_view(), name='endorsement-list'),
            url(r'^create-endorsement/$', self.endorsement_create_view.as_view(), name='endorsement-create'),
            url(r'^delete-endorsement/(?P<pk>\d+)/$', self.endorsement_delete_view.as_view(), name='endorsement-delete'),
            url(r'^update-endorsement/(?P<pk>\d+)/$', self.endorsement_update_view.as_view(), name='endorsement-update'),
            url(r'^view-endorsement/(?P<pk>\d+)/$', self.endorsement_detail_view.as_view(), name='endorsement-detail'),
        ]
        return self.post_process_urls(urls)


application = CampaignDashboardConfig()

