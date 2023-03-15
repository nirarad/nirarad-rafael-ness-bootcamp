import json
import os
import uuid

from utils.rabbitmq.rabbitmq_send import RabbitMQ
from dotenv import load_dotenv

# For local running ONLY!
load_dotenv('../../tests/DATA/.env.test')


def rabbit_mq_publish(routing_key, body_to_send):
    with RabbitMQ() as mq:
        published_body = mq.publish(exchange='eshop_event_bus',
                                    routing_key=routing_key,
                                    body=json.dumps(body_to_send))
    return published_body


def create_order(body_to_send):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: create_order
    Description: Function of Basket simulator.
                 1.Sends message to RabbitMQ queue Ordering to create order
    :param body_to_send: body to send in message
    :return: sent body with server date corrected
    """
    if body_to_send is None:
        raise Exception('Message body is None.')
    # Sending message to RabbitMQ queue Ordering
    return rabbit_mq_publish(os.getenv('CREATE_ORDER_ROUTING_KEY'), body_to_send)


def confirm_stock(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: confirm_stock
    Description: Function of Catalog simulator.
                 1.Sends message to RabbitMQ queue Ordering that items in stock
                 P.S:
                 It is response message for request of Ordering service to check items in stock.
    :param date: server generated date
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    """
    body = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": date
    }
    rabbit_mq_publish(os.getenv('CONFIRM_STOCK_ROUTING_KEY'), body)


def reject_stock(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: reject_stock
    Description: Function of Catalog simulator.
                 1.Sends message to RabbitMQ queue Ordering that items not in stock
                 P.S:
                 It is response message for request of Ordering service to check items in stock.
    :param date: server generated date
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    """
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
    body = {
        "OrderId": order_id,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": x_requestid,
        "CreationDate": date
    }
    rabbit_mq_publish(os.getenv('REJECT_STOCK_ROUTING_KEY'), body)


def payment_succeeded(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: payment_succeeded
    Description: Function of Payment simulator.
                 1.Sends message to RabbitMQ queue Ordering that order payment succeeded.
                 P.S:
                 It is response message for request of Ordering service to order payment.
    :param date: order date,must be the same as in order,cause live processing
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
    body_to_send = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": date
    }
    rabbit_mq_publish(os.getenv('PAYMENT_SUCCEEDED_ROUTING_KEY'), body_to_send)


def payment_failed(order_id, x_requestid, date):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: payment_failed
    Description: Function of Payment simulator.
                 1.Sends message to RabbitMQ queue Ordering that order payment failed.
                 P.S:
                 It is response message for request of Ordering service to order payment.
    :param date: order date,must be the same as in order,cause live processing
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
    body = {
        "OrderId": order_id,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": x_requestid,
        "CreationDate": date
    }
    rabbit_mq_publish(os.getenv('PAYMENT_FAILED_ROUTING_KEY'), body)


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
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
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
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
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
    # order_uuid = str(uuid.uuid4())
    # datareader = JSONDataReader(os.getenv('ORDERS_PATH'))
    # body = datareader.get_json_order('alice_normal_order', order_uuid)  # normal order
    # # create_order(body)  # normal order
    # # # body = datareader.get_json_order('alice_order_empty_list', order_uuid)  # empty list
    # # # create_order(body)  # empty list
    # # # body = datareader.get_json_order('alice_order_0_quantity', order_uuid)  # 0 quantity
    # # # create_order(body)  # 0 quantity
    # # payment_succeeded(281, 'd5129184-2006-419d-b922-6915718ef1a4')
    # sent_body = create_order(body)  # normal order
    # d = eval(sent_body)
    # payment_succeeded(317, "2f27dd08-6360-408d-83c7-5d7cca1d44a9", d['CreationDate'])
    payment_succeeded(319, 'f302f5a8-522a-409f-b4dd-76f9cfb7aa5e', '2023-03-13T15:43:29.2988114Z')

    # print('\n')
    # print(k)
    pass
