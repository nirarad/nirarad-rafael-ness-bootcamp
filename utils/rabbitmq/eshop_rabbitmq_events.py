import json
import os
import uuid

from utils.rabbitmq.rabbitmq_send import RabbitMQ
from dotenv import load_dotenv

from utils.testcase.jsondatareader import JSONDataReader

# For local running ONLY!
load_dotenv('../../.env.test')


def rabbit_mq_publish(routing_key, body_to_send):
    with RabbitMQ() as mq:
        published_body = mq.publish(exchange='eshop_event_bus',
                                    routing_key=routing_key,
                                    body=json.dumps(body_to_send))
    return published_body





def status_changed_to_stock(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: status_changed_to_stock
    Description: Function sends to Payment queue message that stock confirmed.
                 1.Sends message to RabbitMQ queue Ordering that order payment failed.
    :param date: order date,must be the same as in order,cause live processing
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    load_dotenv('/.env.test')
    body = \
        {
            "OrderId": order_id,
            "OrderStatus": "stockconfirmed",
            "BuyerName": "alice",
            "Id": x_requestid,
            "CreationDate": date
        }

    rabbit_mq_publish(os.getenv('PAYMENT_BINDING'), body)


def status_changed_to_awaitingvalidation(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: status_changed_to_stock
    Description: Function sends to Payment queue message that stock confirmed.
                 1.Sends message to RabbitMQ queue Ordering that order payment failed.
    :param date: order date,must be the same as in order,cause live processing
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    load_dotenv('/.env.test')
    body = \
        {
            "OrderId": order_id,
            "OrderStatus": "awaitingvalidation",
            "BuyerName": "alice",
            "Id": x_requestid,
            "CreationDate": date
        }

    rabbit_mq_publish(os.getenv('CATALOG_BINDING'), body)


# def change_status_awaiting_validation(x_requestid=None, order_number=0):
#     body = {
#         "OrderId": order_number,
#         "OrderStatus": "awaitingvalidation",
#         "BuyerName": "alice",
#         "OrderStockItems": [
#             {
#                 "ProductId": 1,
#                 "Units": 1
#             }
#         ],
#         "Id": x_requestid,
#         "CreationDate": "2023-03-05T14:27:28.8042812Z"
#     }
#     rabbit_mq_publish('OrderStatusChangedToAwaitingValidationIntegrationEvent', body)


if __name__ == '__main__':
    order_uuid = str(uuid.uuid4())
    datareader = JSONDataReader(os.getenv('ORDERS_PATH'))
    body = datareader.get_json_order('alice_normal_order', order_uuid)  # normal order
    pass
