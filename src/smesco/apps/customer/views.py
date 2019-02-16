from django import http
from django.conf import settings
from django.views import generic
from django.contrib import messages
from django.utils.encoding import force_text
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login as auth_login
from django.core.exceptions import ObjectDoesNotExist
from oscar.apps.payment.exceptions import PaymentError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from oscar.apps.order import exceptions as order_exceptions
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from oscar.core.compat import get_user_model
from oscar.core.loading import (
    get_class, get_classes, get_model, get_profile_class)

from apps.customer.tokens import account_activation_token
from oscar.apps.customer import signals
from oscar.apps.customer.views import OrderDetailView as OriginalOrderDetailView
from apps.payment.utils import ipay_signature_creator, get_complete_url
from apps.partner_api.tasks import send_registration_email, send_registration_activation_email

PageTitleMixin, RegisterUserMixin = get_classes(
    'customer.mixins', ['PageTitleMixin', 'RegisterUserMixin'])
Dispatcher = get_class('customer.utils', 'Dispatcher')
EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes(
    'customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm',
                       'OrderSearchForm'])
OrderStatusForm = get_class('dashboard.orders.forms', 'OrderStatusForm')
EventHandler = get_class('order.processing', 'EventHandler')
ProfileForm, PasswordChangeForm = get_classes('customer.forms', ['ProfileForm', 'PasswordChangeForm'])

Email = get_model('customer', 'Email')
Order = get_model('order', 'Order')
Product = get_model('catalogue', 'Product')
UserAddressForm = get_class('address.forms', 'UserAddressForm')
UserAddress = get_model('address', 'UserAddress')

User = get_user_model()


class MultipleFormsMixin(FormMixin):
    """
    A mixin that provides a way to show and handle several forms in a
    request.
    """
    form_classes = {} # set the form classes as a mapping

    def get_form_classes(self):
        return self.form_classes

    def get_form_kwargs(self, **kwargs):
        data = super(MultipleFormsMixin, self).get_form_kwargs(**kwargs)
        data['user'] = self.request.user
        return data

    def get_forms(self, form_classes):
        return dict([(key, klass(**self.get_form_kwargs()))
                     for key, klass in form_classes.items()])

    def forms_valid(self, forms):
        return super(MultipleFormsMixin, self).form_valid(forms)

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(form=forms))


class ProcessMultipleFormsView(ProcessFormView):
    """
    A mixin that processes multiple forms on POST. Every form must be
    valid.
    """
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(form=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        action = self.request.POST['action']
        form = forms.get(action, None)
        if form and form.is_valid():
            form.save()
            return self.forms_valid(form)
        else:
            messages.error(request, 'Maaf terjadi kesalahan saat melakukan update')
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultipleFormsMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultipleFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaing several forms, and rendering a template response.
    """


class AccountAuthView(RegisterUserMixin, generic.TemplateView):
    """
    This is actually a slightly odd double form view that allows a customer to
    either login or register.
    """
    template_name = 'customer/login.html'
    login_prefix = 'login'
    login_form_class = EmailAuthenticationForm
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super(AccountAuthView, self).get(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(AccountAuthView, self).get_context_data(*args, **kwargs)
        if 'login_form' not in kwargs:
            ctx['login_form'] = self.get_login_form()
        return ctx

    def post(self, request, *args, **kwargs):
        # Use the name of the submit button to determine which form to validate
        if u'login_submit' in request.POST:
            return self.validate_login_form()

        return http.HttpResponseBadRequest()

    # LOGIN

    def get_login_form(self, bind_data=False):
        return self.login_form_class(
            **self.get_login_form_kwargs(bind_data))

    def get_login_form_kwargs(self, bind_data=False):
        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.login_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
        }
        if bind_data and self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def validate_login_form(self):
        form = self.get_login_form(bind_data=True)
        if form.is_valid():
            user = form.get_user()

            # Grab a reference to the session ID before logging in
            old_session_key = self.request.session.session_key

            auth_login(self.request, form.get_user())

            # Raise signal robustly (we don't want exceptions to crash the
            # request handling). We use a custom signal as we want to track the
            # session key before calling login (which cycles the session ID).
            signals.user_logged_in.send_robust(
                sender=self, request=self.request, user=user,
                old_session_key=old_session_key)

            msg = self.get_login_success_message(form)
            if msg:
                messages.success(self.request, msg)

            return redirect(self.get_login_success_url(form))

        ctx = self.get_context_data(login_form=form)
        return self.render_to_response(ctx)

    def get_login_success_message(self, form):
        return

    def get_login_success_url(self, form):
        redirect_url = form.cleaned_data['redirect_url']
        if redirect_url:
            return redirect_url

        # Redirect staff members to dashboard as that's the most likely place
        # they'll want to visit if they're logging in.
        if self.request.user.is_staff:
            return reverse_lazy('dashboard:index')

        return settings.LOGIN_REDIRECT_URL


class AccountRegistrationView(RegisterUserMixin, generic.TemplateView):
    template_name = 'customer/registration.html'
    registration_prefix = 'register'
    registration_form_class = EmailUserCreationForm
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super(AccountRegistrationView, self).get(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(AccountRegistrationView, self).get_context_data(
            *args, **kwargs)
        if 'registration_form' not in kwargs:
            ctx['registration_form'] = self.get_registration_form()
        return ctx

    def post(self, request, *args, **kwargs):
        # Use the name of the submit button to determine which form to validate
        if u'registration_submit' in request.POST:
            return self.validate_registration_form(request)

        return http.HttpResponseBadRequest()

    def get_logged_in_redirect(self):
        return reverse('customer:summary')

    def form_valid(self, form):
        self.register_user(form)
        return redirect(form.cleaned_data['redirect_url'])

    # REGISTRATION

    def get_registration_form(self, bind_data=False):
        return self.registration_form_class(
            **self.get_registration_form_kwargs(bind_data))

    def get_registration_form_kwargs(self, bind_data=False):
        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.registration_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
        }
        if bind_data and self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def validate_registration_form(self, request):
        form = self.get_registration_form(bind_data=True)
        if form.is_valid():
            scheme = request.scheme
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            to_email = form.cleaned_data.get('email')
            send_registration_email.delay(to_email, user.id, scheme, current_site.domain, )
            messages.success(self.request, 'Silahkan periksa email anda untuk melakukan aktivasi akun.')
            return redirect(reverse_lazy('customer:login'))

        ctx = self.get_context_data(registration_form=form)
        return self.render_to_response(ctx)


class ProfileView(PageTitleMixin, MultipleFormsView):
    template_name = 'customer/profile/profile.html'
    page_title = _('Profile')
    active_tab = 'profile'
    success_url = reverse_lazy('customer:profile-view')
    form_classes = {
        'profile_form': ProfileForm,
        'change_password_form': PasswordChangeForm,
    }

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        action = self.request.POST['action']
        form = forms.get(action, None)
        if form and form.is_valid():
            form.save()
            user = User.objects.get(pk=request.user.id)
            update_session_auth_hash(self.request, user)
            return self.forms_valid(form)
        else:
            messages.error(request, 'Maaf terjadi kesalahan saat melakukan update')
            return self.forms_invalid(forms)

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        ctx['profile_fields'] = self.get_profile_fields(self.request.user)
        return ctx

    def get_profile_fields(self, user):
        field_data = []

        # Check for custom user model
        for field_name in User._meta.additional_fields:
            if field_name in ('user', 'id', 'work'):
                continue
            field_data.append(
                self.get_model_field_data(user, field_name))

        # Check for profile class
        profile_class = get_profile_class()
        if profile_class:
            try:
                profile = profile_class.objects.get(user=user)
            except ObjectDoesNotExist:
                profile = profile_class(user=user)

            field_names = [f.name for f in profile._meta.local_fields]
            for field_name in field_names:
                if field_name in ('user', 'id', 'work'):
                    continue
                field_data.append(
                    self.get_model_field_data(profile, field_name))

        return field_data

    def get_model_field_data(self, model_class, field_name):
        """
        Extract the verbose name and value for a model's field value
        """
        field = model_class._meta.get_field(field_name)
        if field.choices:
            value = getattr(model_class, 'get_%s_display' % field_name)()
        else:
            value = getattr(model_class, field_name)
        return {
            'name': getattr(field, 'verbose_name'),
            'value': value,
        }


class AddressListView(PageTitleMixin, MultipleFormsView):
    """Customer address book"""
    form_classes = {'user_address_form': UserAddressForm}
    template_name = 'customer/address/address_list.html'
    paginate_by = settings.OSCAR_ADDRESSES_PER_PAGE
    active_tab = 'addresses'
    page_title = _('Address Book')
    success_url = reverse_lazy('customer:address-list')

    def get_addresses(self):
            return self.request.user.addresses.filter(
                country__is_shipping_country=True).order_by(
                '-is_default_for_billing')

    def get_context_data(self, **kwargs):
        ctx = super(AddressListView, self).get_context_data(**kwargs)
        ctx['addresses'] = [UserAddressForm(user=self.request.user,
                                            instance=address) for address in self.get_addresses()]
        return ctx


class AddressNewDeleteView(generic.RedirectView):
    """
    Sets an address as default_for_(billing|shipping)
    """
    url = reverse_lazy('customer:address-list')
    permanent = False

    def get(self, request, pk=None, action=None, *args, **kwargs):
        address = get_object_or_404(UserAddress, user=self.request.user,
                                    pk=pk)
        next_page = request.GET.get('next', None)
        if next_page:
            self.url = next_page
        address.delete()
        messages.success(request, _('Alamat Berhasil dihapus'))
        return super(AddressNewDeleteView, self).get(
            request, *args, **kwargs)


class AddressChangeStatusView(generic.RedirectView):
    """
    Sets an address as default_for_(billing|shipping)
    """
    url = reverse_lazy('customer:address-list')
    permanent = False

    def get(self, request, pk=None, action=None, *args, **kwargs):
        address = get_object_or_404(UserAddress, user=self.request.user,
                                    pk=pk)
        #  We don't want the user to set an address as the default shipping
        #  address, though they should be able to set it as their billing
        if address.country.is_shipping_country:
            if action == 'default_for_shipping_address':
                self.url = reverse_lazy('checkout:shipping-address')
                setattr(address, 'is_default_for_billing', True)
                setattr(address, 'is_default_for_shipping', True)
            elif action == 'default_for_billing':
                setattr(address, 'is_default_for_billing', True)
                setattr(address, 'is_default_for_shipping', True)
            else:
                setattr(address, 'is_%s' % action, True)
        else:
            messages.error(request, _('We do not ship to this country'))
        #  address.
        address.save()
        return super(AddressChangeStatusView, self).get(
            request, *args, **kwargs)


class OrderDetailView(OriginalOrderDetailView):

    def get_context_data(self, **kwargs):
        ctx = super(OrderDetailView, self).get_context_data(**kwargs)
        order = self.get_object()
        ctx['payment_url'] = getattr(settings, 'IPAY_PAYMENT_URL', None)
        ctx['merchant_code'] = getattr(settings, 'IPAY_MERCHANT_CODE', None)
        ctx['response_url'] = get_complete_url(self.request, 'payment-response', order.number,
                                               'customer:order')
        ctx['backend_url'] = get_complete_url(self.request, 'payment-notification', order.number)
        ctx['signature_key'] = ipay_signature_creator(order.number, order.total_incl_tax)
        ctx['place_status'] = getattr(settings, 'ORDER_STATUS_PLACED', None)
        return ctx


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        current_site = get_current_site(request)
        send_registration_activation_email.delay(user.id, current_site.domain)
        messages.success(request, 'Terima kasih telah melakukan konfirmasi. Sekarang anda dapat login.')
    else:
        messages.success(request, 'Maaf, link aktivasi tidak valid!')

    return redirect(reverse_lazy('customer:login'))


@login_required
def change_order_status(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.filter(number=data['order']).first()
        form = OrderStatusForm(order=order, data=data)
        if not form.is_valid():
            return redirect('customer:order-list')
        old_status, new_status = order.status, form.cleaned_data['new_status']
        reason = data.get('reason', '(no reason given)')
        handler = EventHandler(request.user)
        success_msg = _(
            "Order status #%(order_number)s changed from '%(old_status)s' to "
            "'%(new_status)s' with reason '%(reason)s'") % {'order_number': data['order'],
                                                            'old_status': old_status,
                                                            'new_status': new_status,
                                                            'reason': reason}

        if order.user != request.user:
            return redirect('promotions:home')

        try:
            # TODO: use this if IPAY open cancel API
            # if new_status == STATUS_CANCELED:
                # cancel_payment = process_cancel_order(request)

                # if cancel_payment['status_code'] != OK:
                #     messages.error(
                #         request, _("Cannot change order status because cancel payment was unsuccessful"))
                #     return redirect('customer:order-list')
            #     send_email_order.delay(STATUS_CANCELED, order.id)
            #
            # if new_status == STATUS_COMPLETED:
            #     send_email_order.delay(STATUS_COMPLETED, order.id)

            handler.handle_order_status_change(
                order, new_status, note_msg=success_msg)

        except PaymentError as e:
            messages.error(
                request, _("Unable to change order status due to "
                           "payment error: %s") % e)
        except order_exceptions.InvalidOrderStatus as e:
            messages.error(
                request, _("Unable to change order status as the requested "
                           "new status is not valid"))

        return redirect('customer:order-list')


def update_address(request, pk):
    url = 'customer:address-list'
    if request.method == 'POST':
        data = request.POST
        next_page = request.GET.get('next', None)
        if next_page:
            url = next_page
        address = UserAddress.objects.filter(pk=pk).first()
        form = UserAddressForm(request.user, data, instance=address)
        if form.is_valid():
            form.save()
            messages.success(
                request, _("Berhasil update alamat"))

            return redirect(url)

        messages.error(
            request, _("Gagal update alamat, mohon cek kembali isian Anda"))
        return redirect(url)
