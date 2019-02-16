from django.core.validators import RegexValidator
from django.db import models
from oscar.apps.address.abstract_models import AbstractUserAddress
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.core import exceptions


class State(TimeStampedModel):
    country = models.ForeignKey('address.Country', related_name='states', on_delete=models.CASCADE, default="")
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "state"


class District(TimeStampedModel):
    state = models.ForeignKey(State, related_name='districts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'district'
        unique_together = ('state', 'name')


class Subdistrict(TimeStampedModel):
    district = models.ForeignKey(District, related_name='subdistricts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'subdistrict'
        unique_together = ('district', 'name')


class Village(TimeStampedModel):
    subdistrict = models.ForeignKey(Subdistrict, related_name='villages', on_delete=models.CASCADE)
    postcode = models.CharField(_('Postcode'), max_length=10, default="")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'village'
        unique_together = ('subdistrict', 'name')


class UserAddress(AbstractUserAddress):
    line1 = models.CharField(_("Alamat"), max_length=255)
    province = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, verbose_name=_("Provinsi"))
    regency_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, verbose_name=_("Kota/Kabupaten"))
    subdistrict = models.ForeignKey(Subdistrict, on_delete=models.SET_NULL, null=True, verbose_name=_("Kecamatan"))
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, verbose_name=_("Desa/Kelurahan"))

    country = models.ForeignKey(
        'address.Country',
        on_delete=models.CASCADE,
        verbose_name=_("Country"), default="ID")

    base_fields = hash_fields = ['salutation', 'complete_address', 'postcode', 'phone_number']

    def get_field_values(self, fields):
        field_values = []
        for field in fields:
            if field == 'title':
                value = self.get_title_display()
            elif field == 'country':
                try:
                    value = self.country.printable_name
                except exceptions.ObjectDoesNotExist:
                    value = ''
            elif field == 'salutation':
                value = self.salutation
            elif field == 'complete_address':
                value = f'{self.line1}, {self.village.name}, {self.subdistrict.name}, \
                {self.regency_district.name} - {self.province.name}'
            elif field == 'phone_number':
                value = 'Telp: ' + str(self.phone_number) if self.phone_number else 'Telp: -'
            elif field == 'province':
                value = self.province.name
            elif field == 'regency_district':
                value = self.regency_district.name
            elif field == 'subdistrict':
                value = self.subdistrict.name
            elif field == 'village':
                value = self.village.name
            else:
                value = getattr(self, field)
            field_values.append(value)
        return field_values

    def get_address_field_values(self, fields):
        field_values = [f.strip() for f in self.get_field_values(fields) if f]
        return field_values

    def active_address_fields(self):
        return self.get_address_field_values(self.base_fields)

    @property
    def salutation(self):
        """
        Name (including title)
        """
        return self.join_fields(
            ('first_name', 'last_name'),
            separator=u" ")

    def save(self, *args, **kwargs):
        self.hash = self.generate_hash()
        if not self.id:
            self.is_default_for_shipping = True
            self.is_default_for_billing = True
        self._ensure_defaults_integrity()

        super(AbstractUserAddress, self).save(*args, **kwargs)


from oscar.apps.address.models import *  # noqa isort:skip
