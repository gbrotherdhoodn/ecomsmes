import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.order.models import Order
from apps.payment.utils import on_payment_updated

log = logging.getLogger('smesco')


@csrf_exempt
def notification(request):
    request_user = f"{request.META.get('USER')}@{request.META.get('HTTP_HOST')}"
    if request.method == 'POST':
        log.info(
            f"POST notification request for order {json.loads(request.body).get('order_id')}. Issuer: {request_user}"
        )

        try:
            order = Order.objects.get(number=json.loads(request.body).get('order_id'))

            return on_payment_updated(order=order, request=request)

        except ObjectDoesNotExist:
            log.info(f"Cant find order {json.loads(request.body).get('order_id')} on DB")

            return JsonResponse({"message": f"Not Found"}, status=503)

        except Order.DoesNotExist:
            log.info(f"Cant find order {json.loads(request.body).get('order_id')} on DB")
            return JsonResponse({"message": f"Not Found"}, status=503)

        except Exception as e:
            log.error(f"Something Happened : {e}")
            raise e

    log.info(f"notification request for order {json.loads(request.body).get('order_id')} Success")
    return JsonResponse({"message": "success-"})
