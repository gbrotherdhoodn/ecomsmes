import urllib
import django_filters

from django.conf import settings
from django.core import serializers
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters import FilterSet
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.utils.http import urlquote
from oscar.apps.catalogue.views import ProductDetailView as CustomProductDetailView
from django.utils.translation import ugettext_lazy as _
from django import forms

from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')


def add_delete_product_to_wishlist(request, *args, **kwargs):
    data = args[0]
    if data.method != 'GET':
        return HttpResponseBadRequest
    if not data.user.is_authenticated:
        return HttpResponseBadRequest({
            "status": "failed",
            "message": "user should login"
        })
    product_slug = kwargs.get('product_slug')
    product_pk = kwargs.get('product_pk')
    product = get_object_or_404(Product, slug=product_slug, pk=product_pk)
    wishlist = data.user.wishlists.last()
    if not wishlist:
        wishlist = data.user.wishlists.create()

    if not wishlist.is_allowed_to_edit(data.user):
        return HttpResponseBadRequest({
            "status": "failed",
            "message": "wish list not editable"
        })
    product_in_wishlist = wishlist.lines.filter(product_id=product_pk)
    if product_in_wishlist:
        product_in_wishlist.delete()
    else:
        wishlist.add(product)
    return JsonResponse({
        "status": "success",
        "message": "wishlist updated"
    })


def product_review_list(request, *args, **kwargs):
    data = args[0]
    if data.method != 'GET':
        return HttpResponseBadRequest
    product_slug = kwargs.get('product_slug')
    product_pk = kwargs.get('product_pk')
    product = get_object_or_404(Product, slug=product_slug, pk=product_pk)
    review_list = ProductReview.objects.approved().filter(product=product)
    page = data.GET.get('page', 1)
    paginator = Paginator(review_list, settings.OSCAR_REVIEWS_PER_PAGE)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    now_page = reviews.number
    return JsonResponse({
        "status": "success",
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "next_page": now_page + 1 if now_page < paginator.num_pages else None,
        "previous_page": now_page - 1 if now_page > 1 else None,
        "data": serializers.serialize('json', reviews.object_list)
    })


class ProductReviewForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)

    def __init__(self, product, user=None, *args, **kwargs):
        super(ProductReviewForm, self).__init__(*args, **kwargs)
        self.instance.product = product
        if user and user.is_authenticated:
            self.instance.user = user
            del self.fields['name']
            del self.fields['email']

    class Meta:
        model = ProductReview
        fields = ('title', 'score', 'body', 'name', 'email')


class ProductReviewTweak(forms.Form):
    STATUS_CHOICES = (
        (0, _("0")),
        (1, _("1")),
        (2, _("2")),
        (3, _("3")),
        (4, _("4")),
        (5, _("5")),
    )
    title = forms.CharField(required=True, label='Judul')
    score = forms.ChoiceField(required=True, label='Rating', choices=STATUS_CHOICES, initial='', widget=forms.Select())
    body = forms.CharField(required=True, label='Komentar', widget=forms.Textarea)


class ProductFilter(FilterSet):
    warna = django_filters.NumberFilter(field_name='attribute_values__value_option_id')
    ukuran = django_filters.NumberFilter(field_name='attribute_values__value_option_id')

    class Meta:
        model = Product
        fields = ['attribute_values']


class ProductDetailView(CustomProductDetailView):
    enforce_parent = False
    query_params = {}
    form = ProductReviewTweak
    response = None

    current_product = True
    current_attribute = None

    accepted_query_params = ["warna", "ukuran"]

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['alert_form'] = self.get_alert_form()
        ctx['has_active_alert'] = self.get_alert_status()
        ctx['query_params'] = self.query_params
        ctx['forms'] = self.form()
        ctx['is_variant_available'] = self.current_product
        ctx['attribute_current'] = self.current_attribute
        ctx['meta'] = self.get_object().as_meta()

        if kwargs.get('forms'):
            ctx['forms'] = kwargs.get('forms')

        return ctx

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            ProductReview.objects.create(
                title=data.get('title'),
                score=data.get('score'),
                name=f'{request.user.first_name} {request.user.last_name}',
                email=request.user.email,
                product=self.get_object(),
                body=data.get('body'),
                user=self.request.user
            )

            from urllib.parse import urlencode
            return HttpResponseRedirect(f"{self.get_object().get_absolute_url()}?{urlencode(self.query_params)}")

        self.object = self.get_object()
        context = self.get_context_data(object=self.object, forms=form)
        return self.render_to_response(context)

    def get_cleaned_query_params(self, request):
        p = request.GET.copy()
        for x in request.GET.keys():
            if x not in self.accepted_query_params and not p.get(x).isdigit():
                p.pop(x, None)
        return p

    def force_query_params(self, product):
        # GET available variant from db
        variant_dict = self.attribute_to_dict(product)
        new = {}
        for key in variant_dict.keys():
            if key in self.accepted_query_params:
                new[key] = variant_dict.get(key)
        url_params = urllib.parse.urlencode(new)

        return url_params

    def set_params_url(self, product):
        result = {}
        if product:
            attribute_codes = product.attribute_values.values_list('attribute__code', 'value_option_id').all()
            for attribute in attribute_codes:
                result[attribute[0]] = [str(attribute[1])]
        else:
            result = dict(self.request.GET.copy())
        return result

    def redirect_if_necessary(self, current_path, product):
        if not product:
            return None
        if self.enforce_parent and product.is_child:
            return HttpResponsePermanentRedirect(
                product.parent.get_absolute_url())
        if self.enforce_paths:
            expected_path = product.get_absolute_url()
            if expected_path != urlquote(current_path):
                expected_path = product.get_absolute_url()
                params_ = self.force_query_params(product)
                return HttpResponsePermanentRedirect(f"{expected_path}?{params_}")

    def process_param(self, product):

        previous_product = product
        parent_id = previous_product.parent_id
        product = ProductFilter(self.request.GET, queryset=Product.objects.all())

        if product.qs:
            if product.qs.filter(parent_id=parent_id):
                return product.qs.filter(parent_id=parent_id).first()
        else:
            return False

    def try_find_other_sibling(self, product):
        product = self.process_param(product)

        if product:
            self.detect_not_match(product)
            return product
        else:
            self.current_product = False

    def attribute_to_dict(self, product):
        result = {}
        attribute_codes = product.attribute_values.values_list('attribute__code', 'value_option_id').all()
        for attribute in attribute_codes:
            result[attribute[0]] = attribute[1]
        return result

    def detect_not_match(self, product):
        """
        tell frontnend if current product doesnt have
        :param product: current product
        :return: if variant not match 100%
        """
        current_params = self.get_cleaned_query_params(self.request)
        attribute_dict = self.attribute_to_dict(product)
        check_result = []

        for key in current_params:
            # attribute_code stroed as int on database
            if attribute_dict.get(key) != int(current_params.get(key)):
                check_result.append(False)
            else:
                check_result.append(True)
                self.current_product = True

        if False in check_result:
            self.current_product = False

    def get(self, request, **kwargs):
        product = get_object_or_404(Product, id=self.kwargs.get('pk'))
        self.current_attribute = self.attribute_to_dict(product)
        params = self.get_cleaned_query_params(request)

        if product.is_parent:
            product = Product.objects.filter(parent=product).first()
            self.current_attribute = self.attribute_to_dict(product)

        if params:
            product = self.try_find_other_sibling(product)
            if product:
                self.current_attribute = self.attribute_to_dict(product)

        redirect = self.redirect_if_necessary(request.path, product)

        if redirect is not None:
            return redirect

        self.query_params = self.set_params_url(product)
        response = super(ProductDetailView, self).get(request, **self.kwargs)
        return response


def helper_session_handle_product(request, parent_id):
    if not request.session.get('product_parent', None):
        request.session['product_parent'] = parent_id
        return True
    return parent_id == request.session.get('product_parent')
