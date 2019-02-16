import json
import logging

import requests
from django.conf import settings
from ..decorators import run_async

logger = logging.getLogger(__name__)


class KgxClient(object):
    """KG-Xpress Client"""
    def __init__(self, base_url, username, password, origin_zip_code):
        self.auth = (username, password)
        self.origin_zip_code = origin_zip_code
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}

    @run_async
    def check_rate(self, zip_code, weight):
        url = '%s/check_rate' % (self.base_url,)
        params = {
            "origin_zipcode": self.origin_zip_code,
            "destination_zipcode": zip_code,
            "weight": weight
        }

        return self.kgx_client(url, self.headers, params, 'post')

    @run_async
    def create_order(self, order, weight):
        url = '%s/create_order' % (self.base_url,)
        pickup_type = "reg"

        params = {
            "web_order_id": order.number,
            "sender": settings.SHIPPING_SENDER,
            "origin": settings.SHIPPING_ORIGIN,
            "recipient": {
                "name": order.shipping_address.name,
                "mobile": "%d%d" % (
                    order.shipping_address.phone_number.country_code,
                    order.shipping_address.phone_number.national_number),
                "email": order.email
            },
            "destination": {
                "address": order.shipping_address.summary,
                "city": order.shipping_address.regency_district.name,
                "state": order.shipping_address.province.name,
                "country": order.shipping_address.country.printable_name,
                "postcode": order.shipping_address.postcode
            },
            "package": {
                "quantity": order.num_items,
                "size": "Motorcycle",
                "weight": weight
            },
            "pickup_type": pickup_type
        }

        return self.kgx_client(url, self.headers, params, 'post')

    @run_async
    def get_order_history(self, order_id):
        url = '%s/get_order_history' % (self.base_url,)
        params = {
            "web_order_id": order_id
        }

        return self.kgx_client(url, self.headers, params, 'get')

    def kgx_client(self, url, headers, params, method):
        try:
            if method == 'post':
                r = requests.post(url, headers=headers, data=json.dumps(params), auth=self.auth)
            else:
                r = requests.get(url, headers=headers, params=params, auth=self.auth)
            response = r.json()
            if r.status_code != 200:
                result = {'status': r.status_code, 'message': response['error']['message'], 'data': None}
            else:
                result = {'status': r.status_code, 'message': 'Success', 'data': response}
        except:
            result = {'status': 500, 'message': 'Something wrong with the system!', 'data': None}

        return result


