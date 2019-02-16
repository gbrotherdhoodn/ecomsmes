from django.test import TestCase, Client
from django.urls import reverse

from oscar.core.loading import get_model

State = get_model('address', 'State')


class AddressViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_load_states(self):
        url = reverse('load-address-states')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/dropdown_list_options.html')

    def test_load_districts(self):
        url = reverse('load-address-districts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/dropdown_list_options.html')

    def test_load_subdistricts(self):
        url = reverse('load-address-subdistricts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/dropdown_list_options.html')

    def test_load_villages(self):
        url = reverse('load-address-villages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/dropdown_list_options.html')

    def test_load_postcode(self):
        url = reverse('load-address-postcode')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
