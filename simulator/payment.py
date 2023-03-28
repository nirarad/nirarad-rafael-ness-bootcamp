import uuid
from utils.helper_functions import rabbit_mq_publish, current_time


def payment_success(order_number):
    body = {
        "OrderId": order_number,
        "Id": str(uuid.uuid4()),
        "CreationDate": current_time()
    }
    rabbit_mq_publish('OrderPaymentSucceededIntegrationEvent', body)


def payment_failed(order_number):
    body = {
        "OrderId": order_number,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": str(uuid.uuid4()),
        "CreationDate": current_time()
    }
    rabbit_mq_publish('OrderPaymentFailedIntegrationEvent', body)
