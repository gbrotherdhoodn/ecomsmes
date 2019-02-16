from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_tables2 import SingleTableView
from django.http import HttpResponseRedirect

from oscar.core.loading import get_classes, get_model
from oscar.apps.wishlists.models import Line
from oscar.apps.dashboard.catalogue.views import ProductLookupView as OriginalProductLookupView
from oscar.apps.dashboard.catalogue.views import ProductDeleteView as ProductCustomDeleteView
from oscar.apps.dashboard.catalogue.views import ProductCreateUpdateView as ProductCreateUpdateViewCustom

(ProductForm,
 ProductClassSelectForm,
 ProductSearchForm,
 ProductClassForm,
 CategoryForm,
 StockAlertSearchForm,
 AttributeOptionGroupForm) \
    = get_classes('dashboard.catalogue.forms',
                  ('ProductForm',
                   'ProductClassSelectForm',
                   'ProductSearchForm',
                   'ProductClassForm',
                   'CategoryForm',
                   'StockAlertSearchForm',
                   'AttributeOptionGroupForm'))
(StockRecordFormSet,
 ProductCategoryFormSet,
 ProductImageFormSet,
 ProductRecommendationFormSet,
 ProductAttributesFormSet,
 AttributeOptionFormSet) \
    = get_classes('dashboard.catalogue.formsets',
                  ('StockRecordFormSet',
                   'ProductCategoryFormSet',
                   'ProductImageFormSet',
                   'ProductRecommendationFormSet',
                   'ProductAttributesFormSet',
                   'AttributeOptionFormSet'))
ProductTable, CategoryTable, AttributeOptionGroupTable \
    = get_classes('dashboard.catalogue.tables',
                  ('ProductTable', 'CategoryTable',
                   'AttributeOptionGroupTable'))
(PopUpWindowCreateMixin,
 PopUpWindowUpdateMixin,
 PopUpWindowDeleteMixin) \
    = get_classes('dashboard.views',
                  ('PopUpWindowCreateMixin',
                   'PopUpWindowUpdateMixin',
                   'PopUpWindowDeleteMixin'))
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
StockRecord = get_model('partner', 'StockRecord')
StockAlert = get_model('partner', 'StockAlert')
Partner = get_model('partner', 'Partner')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')


def filter_products(queryset, user):
    """
    Restrict the queryset to products the given user has access to.
    A staff user is allowed to access all Products.
    A non-staff user is only allowed access to a product if they are in at
    least one stock record's partner user list.
    """
    if user.is_staff:
        return queryset

    return queryset.filter(stockrecords__partner__users__pk=user.pk).distinct()


class ProductListView(SingleTableView):

    """
    Dashboard view of the product list.
    Supports the permission-based dashboard.
    """

    template_name = 'dashboard/catalogue/product_list.html'
    form_class = ProductSearchForm
    productclass_form_class = ProductClassSelectForm
    table_class = ProductTable
    context_table_name = 'products'

    def get_context_data(self, **kwargs):
        ctx = super(ProductListView, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        ctx['productclass_form'] = self.productclass_form_class()
        return ctx

    def get_description(self, form):
        if form.is_valid() and any(form.cleaned_data.values()):
            return _('Product search results')
        return _('Products')

    def get_table(self, **kwargs):
        if 'recently_edited' in self.request.GET:
            kwargs.update(dict(orderable=False))

        table = super(ProductListView, self).get_table(**kwargs)
        table.caption = self.get_description(self.form)
        return table

    def get_table_pagination(self, table):
        return dict(per_page=20)

    def filter_queryset(self, queryset):
        """
        Apply any filters to restrict the products that appear on the list
        """
        return filter_products(queryset, self.request.user)

    def get_queryset(self):
        """
        Build the queryset for this list
        """
        queryset = Product.browsable.base_queryset()
        queryset = self.filter_queryset(queryset)
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        """
        Filter the queryset and set the description according to the search
        parameters given
        """
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('upc'):
            # Filter the queryset by upc
            # If there's an exact match, return it, otherwise return results
            # that contain the UPC
            matches_upc = Product.objects.filter(upc=data['upc'])
            qs_match = queryset.filter(
                Q(id__in=matches_upc.values('id')) |
                Q(id__in=matches_upc.values('parent_id')))

            if qs_match.exists():
                queryset = qs_match
            else:
                matches_upc = Product.objects.filter(upc__icontains=data['upc'])
                queryset = queryset.filter(
                    Q(id__in=matches_upc.values('id')) | Q(id__in=matches_upc.values('parent_id')))

        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])

        if data.get('highlight'):
            queryset = queryset.filter(highlight=data['highlight'])

        return queryset


class ProductLookupView(OriginalProductLookupView):

    def get_queryset(self):
        return self.model.objects.exclude_parent()

    def lookup_filter(self, qs, term):
        return qs.filter(Q(title__icontains=term)
                         | Q(parent__title__icontains=term)).exclude(structure='parent')


class ProductDeleteView(ProductCustomDeleteView):

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()

        is_last_child = False
        if self.object.is_child:
            parent = self.object.parent
            is_last_child = parent.children.count() == 1

        self.object.delete()

        if is_last_child:
            self.handle_deleting_last_child(parent)

        Line.objects.filter(product_id=self.object.id).delete()

        return HttpResponseRedirect(self.get_success_url())


class ProductCreateUpdateView(ProductCreateUpdateViewCustom):

    def forms_valid(self, form, formsets):

        if self.creating:
            self.handle_adding_child(self.parent)
        else:
            self.object = form.save()

        for formset in formsets.values():
            formset.save()

        if self.object.is_child:
            ProductCategory.objects.filter(product_id=self.object.id).delete()
            for category in self.object.parent.categories.all():
                ProductCategory.objects.create(product_id=self.object.id, category_id=category.id)
        else:
            children = Product.objects.filter(parent_id=self.object.id)
            for child in children:
                ProductCategory.objects.filter(product_id=child.id).delete()
                for category in self.object.categories.all():
                    ProductCategory.objects.create(product_id=child.id, category_id=category.id)

        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
