from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ungettext
from oscar.core.loading import get_model

from oscar.apps.dashboard.ranges.views import RangeProductListView as RangeProductListViewCustom, \
    RangeUpdateView as RangeUpdateViewCustom, RangeDeleteView as RangeDeleteViewCustom

from apps.dashboard.offers.helper import update_product_offer_range_price

Range = get_model('offer', 'Range')


class RangeProductListView(RangeProductListViewCustom):

    def remove_selected_products(self, request, products):
        range = self.get_range()
        for product in products:
            range.remove_product(product)
            product.save()

        num_products = len(products)
        messages.success(request, ungettext("Removed %d product from range",
                                            "Removed %d products from range",
                                            num_products) % num_products)
        return HttpResponseRedirect(self.get_success_url(request))

    def handle_query_products(self, request, range, form):
        products = form.get_products()
        if not products:
            return

        for product in products:
            range.add_product(product)
            product.save()

        num_products = len(products)
        messages.success(request, ungettext("%d product added to range",
                                            "%d products added to range",
                                            num_products) % num_products)
        dupe_skus = form.get_duplicate_skus()
        if dupe_skus:
            messages.warning(
                request,
                _("The products with SKUs or UPCs matching %s are already "
                  "in this range") % ", ".join(dupe_skus))

        missing_skus = form.get_missing_skus()
        if missing_skus:
            messages.warning(
                request,
                _("No product(s) were found with SKU or UPC matching %s") %
                ", ".join(missing_skus))
        self.check_imported_products_sku_duplicates(request, products)


class RangeUpdateView(RangeUpdateViewCustom):

    def form_valid(self, form):
        self.object = form.save()

        update_product_offer_range_price(self.object)

        return super(RangeUpdateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.included_categories.count() > 0:
            current_cat = sorted([str(x.id) for x in self.object.included_categories.all()])
            new_cat = sorted(request.POST.getlist('included_categories'))

            if current_cat != new_cat:
                self.object.excluded_products.clear()

        return super().post(request, *args, **kwargs)


class RangeDeleteView(RangeDeleteViewCustom):

    def post(self, request, *args, **kwargs):
        try:
            delete = self.delete(request, *args, **kwargs)
            messages.warning(self.request, _("Range deleted"))
            return delete
        except ProtectedError:
            messages.error(
                request, _("Can't delete this range because range is already used in offer discount and/or voucher"))
            return redirect('dashboard:range-list')

    def get_success_url(self):
        return reverse('dashboard:range-list')

