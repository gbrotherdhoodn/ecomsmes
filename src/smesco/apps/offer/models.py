from django.db.models.query import Q
from oscar.apps.offer.abstract_models import AbstractConditionalOffer as CoreAbstractConditionalOffer, \
    AbstractBenefit as CoreAbstractBenefit, AbstractCondition as CoreAbstractCondition, AbstractRange as CoreAbstractRange
from django.db import models
from oscar.models import fields
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_model

ALLAREA = "allarea"
STATE = 'state'
DISTRICT = 'district'
SUBDISTRICT = 'subdistrict'
VILLAGE = 'village'
DESTINATION_TYPE_CHOICES = (
    ('', ''),
    (ALLAREA, 'All Area'),
    (STATE, 'State'),
    (DISTRICT, 'District'),
    (SUBDISTRICT, 'Subdistrict'),
    (VILLAGE, 'Village')
)


class ConditionalOffer(CoreAbstractConditionalOffer):
    def products(self):
        product = get_model('catalogue', 'Product')

        cond_range = self.condition.range
        if cond_range.includes_all_products:
            queryset = product.all
        else:
            queryset = cond_range.all_products()
        return queryset.filter(is_discountable=True).exclude(
            structure=product.PARENT)


class RangeDestination(models.Model):
    name = models.CharField(_("Name"), max_length=128, unique=True)
    slug = fields.AutoSlugField(_("Slug"), max_length=128, unique=True, populate_from="name")
    description = models.TextField(blank=True)
    destination_type = models.CharField(blank=True, max_length=12, choices=DESTINATION_TYPE_CHOICES)
    destination_id = models.IntegerField(blank=True, default=0, null=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'offer'
        db_table = 'offer_range_destination'
        verbose_name = _('Destination Range')
        verbose_name_plural = _('Destination Ranges')

    @property
    def destination_type_name(self):

        if self.destination_type == STATE:
            return "Province"
        elif self.destination_type == DISTRICT:
            return "District"
        elif self.destination_type == SUBDISTRICT:
            return "Subdistrict"
        elif self.destination_type == VILLAGE:
            return "Village"
        elif self.destination_type == ALLAREA:
            return "All Area"


class Benefit(CoreAbstractBenefit):
    range = models.ForeignKey(
        'offer.Range',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Range"))


class Condition(CoreAbstractCondition):
    range_destination = models.ForeignKey(
        "offer.RangeDestination",
        blank=True,
        default=None,
        null=True,
        on_delete=models.CASCADE
    )

    range = models.ForeignKey(
        'offer.Range',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Range"))


class Range(CoreAbstractRange):
    def all_products(self):
        """
        Return a queryset containing all the products in the range

        This includes included_products plus the products contained in the
        included classes and categories, minus the products in
        excluded_products and parent products.
        """
        if self.proxy:
            return self.proxy.all_products()

        product_model = get_model("catalogue", "Product")
        if self.includes_all_products:
            # Filter out child products
            return product_model.browsable.all()

        return product_model.objects.filter(
            Q(id__in=self._included_product_ids()) |
            Q(product_class_id__in=self._class_ids()) |
            Q(productcategory__category_id__in=self._category_ids())
        ).exclude(
            Q(id__in=self._excluded_product_ids()) |
            Q(structure=product_model.PARENT)
        ).distinct()

from oscar.apps.offer.models import *  # noqa isort:skip
