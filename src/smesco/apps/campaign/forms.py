from django import forms


class ContactusForm(forms.Form):
    REGARD_CHOICES = (
        ('Komplain', 'Komplain'),
        ('Pertanyaan', 'Pertanyaan'),
        ('Lainnya', 'Lainnya')
    )
    name = forms.CharField(required=True, label='Nama Lengkap')
    from_email = forms.EmailField(required=True, label='Email')
    in_regard = forms.ChoiceField(choices=REGARD_CHOICES, label='Perihal', initial='',
                                  widget=forms.Select(), required=True)
    message = forms.CharField(widget=forms.Textarea, label='Pesan', required=True)
