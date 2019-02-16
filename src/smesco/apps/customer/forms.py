from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from oscar.apps.customer.forms import (EmailUserCreationForm as RegisterForm,
                                       EmailAuthenticationForm as AuthenticationForm,
                                       ProfileForm as UserForm,
                                       PasswordResetForm as OriginalPasswordResetForm,)
from oscar.core.compat import get_user_model, existing_user_fields
from oscar.core.loading import get_model
from apps.partner_api.tasks import send_reset_password_email

CommunicationEventType = get_model('customer', 'communicationeventtype')

User = get_user_model()


class FormattedDateField(forms.DateField):
    widget = forms.DateInput(format='%Y-%m-%d')

    def __init__(self, *args, **kwargs):
        super(FormattedDateField, self).__init__(*args, **kwargs)
        self.input_formats = ('%Y-%m-%d',)
        self.help_text = 'Format: YYYY-MM-DD'
        self.label = 'Tanggal Lahir'


class ProfileForm(UserForm):
    email = forms.CharField(disabled=True)
    birthdate = FormattedDateField()

    class Meta:
        model = User
        fields = existing_user_fields(['first_name', 'last_name', 'email', 'phone', 'birthdate',
                                       'gender'])


class EmailUserCreationForm(RegisterForm):
    first_name = forms.CharField(required=True, label=_('Nama Depan'))
    last_name = forms.CharField(required=True, label=_('Nama Belakang'))
    email = forms.CharField(required=True, label=_('Email'))
    password1 = forms.CharField(required=True, label=_('Kata Sandi'), widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, label=_('Konfirmasi Kata Sandi'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = existing_user_fields(
            ['first_name', 'last_name', 'email', 'password1', 'password2']
        )


class EmailAuthenticationForm(AuthenticationForm):
    """
    Extends the standard django AuthenticationForm, to support 75 character
    usernames. 75 character usernames are needed to support the EmailOrUsername
    auth backend.
    """
    username = forms.EmailField(label=_('Email'))


class PasswordResetForm(OriginalPasswordResetForm):

    def save(self, domain_override=None, use_https=False, request=None,
             **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        site = get_current_site(request)
        if domain_override is not None:
            site.domain = site.name = domain_override
        email = self.cleaned_data['email']
        active_users = User._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            reset_url = self.get_reset_url(site, request, user, use_https)
            send_reset_password_email.delay(user.id, site.domain, reset_url)
