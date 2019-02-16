from django import forms
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.catalogue.formsets import ProductCategoryFormSet as ProductCategoryFormSetCustom


class ProductCategoryFormSet(ProductCategoryFormSetCustom):

    def clean(self):
        if not self.instance.is_child and self.get_num_categories() == 0:
            raise forms.ValidationError(
                _("Stand-alone and parent products "
                  "must have at least one category"))
        if self.instance.is_child and self.get_num_categories() > 0:
            pass
