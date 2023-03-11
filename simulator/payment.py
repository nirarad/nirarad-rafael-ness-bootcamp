import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def output_create_payment(order_number):
    body = {
        "OrderId": order_number,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }

    return body


def payment_success(order_number):
    body = {
        "OrderId": order_number,
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T15:33:18.1376971Z"
    }
    rabbit_mq_publish('OrderPaymentSucceededIntegrationEvent', body)


def payment_failed(order_number):
    body = {
        "OrderId": order_number,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    rabbit_mq_publish('OrderPaymentFailedIntegrationEvent', body)
