from django.utils.translation import ugettext_lazy as _
from django_tables2 import A, Column, TemplateColumn

from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')


class ProductTable(DashboardTable):
    title = TemplateColumn(
        verbose_name=_('Title'),
        template_name='dashboard/catalogue/product_row_title.html',
        order_by='title',
        accessor=A('title')
    )
    image = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/catalogue/product_row_image.html',
        orderable=False
    )
    product_class = Column(
        verbose_name=_('Product type'),
        accessor=A('product_class'),
        order_by='product_class__name'
    )
    variants = TemplateColumn(
        verbose_name=_("Variants"),
        template_name='dashboard/catalogue/product_row_variants.html',
        orderable=False
    )
    stock_records = TemplateColumn(
        verbose_name=_('Stock records'),
        template_name='dashboard/catalogue/product_row_stockrecords.html',
        orderable=False
    )
    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/catalogue/product_row_actions.html',
        orderable=False
    )

    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        model = Product
        fields = ('upc', 'date_updated')
        sequence = ('image', 'upc', 'title', 'product_class', 'variants',
                    'stock_records', '...', 'date_updated', 'actions')
        order_by = '-date_updated'
