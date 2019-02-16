from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CampaignDashboardConfig(AppConfig):
    label = 'campaign_dashboard'
    name = 'apps.dashboard.campaign'
    verbose_name = _('Campaign Dashboard')
