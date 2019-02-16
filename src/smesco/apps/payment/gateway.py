import http
import logging
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import json
from django.conf import settings
from typing import List
import base64
import requests
from django.http import JsonResponse

log = logging.getLogger('smesco')
TokenResponse = namedtuple('TokenResponse', ['token', 'redirect_url'])


class MidtransAPIError(Exception):
    def __init__(self, messages: List[str]):
        self.messages = messages


class AbstractMidtransClient(metaclass=ABCMeta):
    """ Base class for midtrans clients.
    """

    def __init__(self, server_key: str, sandbox_mode=False, **kwargs):
        self.sandbox_mode = settings.MIDTRANS.get('SANDBOX')
        self.server_key = server_key

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @staticmethod
    def build_request_body(data: dict = None) -> dict:
        template = {
            "transaction_details": {
                "order_id": data.get('order_id'),
                "gross_amount": data.get('gross_amount')
            },
            "enabled_payments": [data.get('payment_method')],
        }
        if data.get("credit_card"):
            template["credit_card"] = data.get("credit_card")
        return template

    def _http_post(self, url, data: dict = None) -> requests.Response:
        h = {'content-type': 'application/json', 'accept': 'application/json'}
        if data is None:
            del h['content-type']
        build = self.build_request_body(data)
        data = json.dumps(build)

        return requests.post(url, auth=(self.server_key, ''), headers=h, data=data)

    def _http_get(self, url):
        return requests.get(url, auth=(self.server_key, ''), headers={'accept': 'application/json', })


class SnapClient(AbstractMidtransClient):

    @property
    def base_url(self):
        return "https://app.sandbox.midtrans.com/snap/v1" if self.sandbox_mode \
            else "https://app.midtrans.com/snap/v1"

    @property
    def js_url(self):
        return "https://app.sandbox.midtrans.com/snap/snap.js" if self.sandbox_mode \
            else "https://app.midtrans.com/snap/snap.js"

    def generate_token(self, order_id: str, gross_amount, payment_method=None) -> TokenResponse:
        gross_amount = int(gross_amount.incl_tax)
        body = {'order_id': order_id,
                'gross_amount': gross_amount}
        if payment_method:
            body['payment_method'] = payment_method
        
        if payment_method == 'credit_card':
            body["credit_card"] = {
                "secure": True,
                "bank": settings.MIDTRANS.get('ACQUIRING_BANK')
                }

        resp = self._http_post(f'{self.base_url}/transactions', body)
        try:
            if 'error_messages' in resp.json():
                raise MidtransAPIError(resp.json()['error_messages'])
            return TokenResponse(**resp.json())
        except Exception as e:
            log.error(f"generate Token Failed : {e}")

            raise e


class ApiClient(AbstractMidtransClient):

    @property
    def base_url(self):
        return "https://api.sandbox.midtrans.com/v2" if self.sandbox_mode \
            else "https://api.midtrans.com/v2"

    def build_header(self):
        encoded = f'{self.server_key}:'.encode('ascii')
        return {"Authorization": base64.b64encode(encoded), "Accept": "application/json"}

    def _http_post(self, url, data: dict = None) -> requests.Response:
        header = {'content-type': 'application/json'}
        header.update(self.build_header())
        return requests.post(f'{self.base_url}/{url}', headers=header)

    def _http_get(self, url: str):
        return requests.get(f'{self.base_url}/{url}', headers=self.build_header())

    def get_order_status(self, order_id):
        try:
            response = self._http_get(f'{order_id}/status')

            if response.status_code == http.HTTPStatus.NOT_FOUND:
                return JsonResponse({"message": "Not Found"}, status=http.HTTPStatus.NOT_FOUND)

            return response.json()

        except Exception as e:
            log.error(f"GET order status Failed : {e}")

            raise e

    def cancel_payment(self, order_id):
        try:
            response = self._http_post(f'{order_id}/cancel')

            if response.status_code == http.HTTPStatus.NOT_FOUND:
                return JsonResponse({"message": "Not Found"}, status=http.HTTPStatus.NOT_FOUND)

            return response.json()

        except Exception as e:
            log.error(f"Failed to Cancel payment for order {order_id} because : {e}")

            raise e
