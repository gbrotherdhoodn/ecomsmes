from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.partner_api.tasks import send_email
from apps.partner_api.client import get_mailchimp_client
from .forms import ContactusForm


def subscribe(request):
    if request.method == 'POST':
        email = request.POST['email_newsletter']

        if not email:
            messages.error(request, settings.NEWSLETTER_FORM_INVALID_EMAIL_MESSAGE)

        validate_email = EmailValidator(settings.NEWSLETTER_FORM_INVALID_EMAIL_MESSAGE, 'invalid')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, settings.NEWSLETTER_FORM_INVALID_EMAIL_MESSAGE)

        mailchimp_client = get_mailchimp_client()

        success, response = mailchimp_client.subscribe_email_list(email)

        if not success:
            messages.error(request, 'Gagal mendaftarkan alamat email Anda.')
        else:
            messages.success(request, 'Terima kasih telah berlangganan. '
                                      'Silahkan periksa inbox email Anda untuk mengkonfirmasi')

    return redirect(reverse_lazy('promotions:home'))


def contact_us_email_view(request):
    if request.method == 'GET':
        form = ContactusForm()
    else:
        form = ContactusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['from_email']
            in_regard = form.cleaned_data['in_regard']
            subject = in_regard + ' - ' + name + ' (' + from_email + ')'
            content = form.cleaned_data['message']
            message = render_to_string('contactus/emails/commtype_contactus_body.html', {
                'name': name,
                'email': from_email,
                'in_regard': in_regard,
                'content': content,
            })
            send_email.delay(subject, settings.OSCAR_TO_EMAIL, message)
            messages.success(request, 'Terima kasih atas email anda. Kami akan segera meresponnya.')
            return redirect(reverse_lazy('contact-us'))

    return render(request, 'contactus/contactus.html', {'form': form})
