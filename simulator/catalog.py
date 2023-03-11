import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def output_verify_item_stock(order_number):
    body = {
        "OrderId": order_number,
        "OrderStatus": "awaitingvalidation",
        "BuyerName": "alice",
        "OrderStockItems": [
            {
                "ProductId": 1,
                "Units": 1
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T14:27:28.8042812Z"
    }

    return body


def in_stock(order_number):
    body = {
        "OrderId": order_number,
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-07T09:52:56.6412897Z"
    }

    rabbit_mq_publish('OrderStockConfirmedIntegrationEvent', body)


def not_in_stock(order_number):
    body = {
        "OrderId": order_number,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T15:51:11.5458796Z"
    }
    rabbit_mq_publish('OrderStockRejectedIntegrationEvent', body)


if __name__ == '__main__':
    in_stock(75)
