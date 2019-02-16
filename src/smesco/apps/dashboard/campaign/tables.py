from django.utils.translation import ugettext_lazy as _
from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import Accessor as A
from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')
Banner = get_model('campaign', 'Banner')
BannerMini = get_model('campaign', 'BannerMini')
Endorsement = get_model('campaign', 'Endorsement')


class BannerTable(DashboardTable):
    image_desktop = TemplateColumn(
        verbose_name=_('Image Desktop'),
        template_name='dashboard/banner/banner_row_image_desktop.html',
        orderable=False)
    image_mobile = TemplateColumn(
        verbose_name=_('Image Mobile'),
        template_name='dashboard/banner/banner_row_image_mobile.html',
        orderable=False)
    title = LinkColumn('dashboard:banner-update', args=[A('pk')])
    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/banner/banner_row_actions.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = Banner
        fields = ('image_desktop', 'image_mobile', 'title', 'number', 'url', 'valid_from', 'valid_until', 'published')
        sequence = ('image_desktop', 'image_mobile', 'title', 'number', 'url', 'valid_from', 'valid_until', 'published')
        order_by = 'number'


class BannerMiniTable(DashboardTable):
    title = LinkColumn('dashboard:banner-mini-update', args=[A('pk')])
    image = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/banner_mini/banner_mini_row_image.html',
        orderable=False)
    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/banner_mini/banner_mini_row_actions.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = BannerMini
        fields = ('title', 'image', 'sort_priority')
        sequence = ('title', 'image', 'sort_priority')
        order_by = 'sort_priority'


class EndorsementTable(DashboardTable):
    name = LinkColumn('dashboard:endorsement-update', args=[A('pk')])
    image = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/endorsements/endorsement_row_image.html',
        orderable=False)
    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/endorsements/endorsement_row_actions.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = Endorsement
        fields = ('name', 'image', 'sort_priority', 'valid_from', 'valid_until', 'published')
        sequence = ('name', 'image', 'sort_priority', 'valid_from', 'valid_until', 'published')
        order_by = 'sort_priority'
