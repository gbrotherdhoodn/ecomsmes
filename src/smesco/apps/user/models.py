from django.core.validators import RegexValidator
from django.db import models
from oscar.apps.customer.abstract_models import AbstractUser


class User(AbstractUser):
    GENDER_CHOICES = (
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    )
    email = models.EmailField('Alamat Email', unique=True)
    first_name = models.CharField('Nama Depan', max_length=255, blank=True)
    last_name = models.CharField('Nama Belakang', max_length=255, blank=True)
    birthdate = models.DateField('Tanggal Lahir', blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\d{8,14}$',
                                 message="field harus number dengan minimal 8 nomor dan tidak lebih dari 14")
    phone = models.CharField('Nomor Telpon/Hp', max_length=14, blank=True, null=True,
                             validators=[phone_regex])
    gender = models.CharField('Jenis Kelamin', max_length=1, choices=GENDER_CHOICES, default='L')
    work = models.CharField('Pekerjaan', max_length=100, blank=True, null=True)
