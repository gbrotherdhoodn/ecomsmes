from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.offers.views import OfferWizardStepView as OfferWizardStepViewCustom, \
    OfferDeleteView as OfferDeleteViewCustom, OfferDetailView as OfferDetailViewCustom
from oscar.core.loading import get_model, get_classes, get_class

from apps.dashboard.offers.helper import update_product_offer_range_price

ConditionalOffer = get_model('offer', 'ConditionalOffer')
Condition = get_model('offer', 'Condition')
Range = get_model('offer', 'Range')
Product = get_model('catalogue', 'Product')
OrderDiscount = get_model('order', 'OrderDiscount')
Benefit = get_model('offer', 'Benefit')
MetaDataForm, ConditionForm, BenefitForm, RestrictionsForm, OfferSearchForm \
    = get_classes('dashboard.offers.forms',
                  ['MetaDataForm', 'ConditionForm', 'BenefitForm',
                   'RestrictionsForm', 'OfferSearchForm'])
OrderDiscountCSVFormatter = get_class(
    'dashboard.offers.reports', 'OrderDiscountCSVFormatter')


class OfferWizardStepView(OfferWizardStepViewCustom):

    def save_offer(self, offer):
        session_offer = self._fetch_session_offer()
        offer.name = session_offer.name
        offer.description = session_offer.description

        benefit = self._fetch_object('benefit')
        if benefit:
            benefit.save()
            offer.benefit = benefit

        condition = self._fetch_object('condition')
        if condition:
            condition.save()
            offer.condition = condition

        offer.save()

        update_product_offer_range_price(offer.benefit.range)

        self._flush_session()

        if self.update:
            msg = _("Offer '%s' updated") % offer.name
        else:
            msg = _("Offer '%s' created!") % offer.name
        messages.success(self.request, msg)

        return HttpResponseRedirect(reverse(
            'dashboard:offer-detail', kwargs={'pk': offer.pk}))


class OfferMetaDataView(OfferWizardStepView):
    step_name = 'metadata'
    form_class = MetaDataForm
    template_name = 'dashboard/offers/metadata_form.html'
    url_name = 'dashboard:offer-metadata'
    success_url_name = 'dashboard:offer-benefit'

    def get_instance(self):
        return self.offer

    def get_title(self):
        return _("Name and description")


class OfferBenefitView(OfferWizardStepView):
    step_name = 'benefit'
    form_class = BenefitForm
    template_name = 'dashboard/offers/benefit_form.html'
    url_name = 'dashboard:offer-benefit'
    success_url_name = 'dashboard:offer-condition'
    previous_view = OfferMetaDataView

    def get_instance(self):
        return self.offer.benefit

    def get_title(self):
        # This is referred to as the 'incentive' within the dashboard.
        return _("Incentive")


class OfferConditionView(OfferWizardStepView):
    step_name = 'condition'
    form_class = ConditionForm
    template_name = 'dashboard/offers/condition_form.html'
    url_name = 'dashboard:offer-condition'
    success_url_name = 'dashboard:offer-restrictions'
    previous_view = OfferBenefitView

    def get_instance(self):
        return self.offer.condition


class OfferRestrictionsView(OfferWizardStepView):
    step_name = 'restrictions'
    form_class = RestrictionsForm
    template_name = 'dashboard/offers/restrictions_form.html'
    previous_view = OfferConditionView
    url_name = 'dashboard:offer-restrictions'

    def form_valid(self, form):
        offer = form.save(commit=False)
        return self.save_offer(offer)

    def get_instance(self):
        return self.offer

    def get_title(self):
        return _("Restrictions")


class OfferDeleteView(OfferDeleteViewCustom):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        range = self.object.benefit.range
        self.object.delete()

        update_product_offer_range_price(range)

        return HttpResponseRedirect(success_url)


class OfferDetailView(OfferDetailViewCustom):

    def post(self, request, *args, **kwargs):
        if 'suspend' in request.POST:
            return self.suspend()
        elif 'unsuspend' in request.POST:
            return self.unsuspend()

    def suspend(self):
        if self.offer.is_suspended:
            messages.error(self.request, _("Offer is already suspended"))
        else:
            self.offer.suspend()
            update_product_offer_range_price(self.offer.benefit.range)
            messages.success(self.request, _("Offer suspended"))
        return HttpResponseRedirect(
            reverse('dashboard:offer-detail', kwargs={'pk': self.offer.pk}))

    def unsuspend(self):
        if not self.offer.is_suspended:
            messages.error(
                self.request,
                _("Offer cannot be reinstated as it is not currently "
                  "suspended"))
        else:
            self.offer.unsuspend()
            update_product_offer_range_price(self.offer.benefit.range)
            messages.success(self.request, _("Offer reinstated"))
        return HttpResponseRedirect(
            reverse('dashboard:offer-detail', kwargs={'pk': self.offer.pk}))
