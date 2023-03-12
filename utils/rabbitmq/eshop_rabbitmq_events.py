import json
import uuid
import os
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.testcase.jsondatagetter import JSONDatagetter
from dotenv import load_dotenv

load_dotenv('../../tests/DATA/.env.test')


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def create_order(x_requestid=None, order_name_json=None):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: create_order
    Description: Function of Basket simulator.
                 1.Gets order from json data.
                 2.Sends message to RabbitMQ queue Ordering to create order
    :param order_name_json: name of order to create
    :param x_requestid: unique id of order generated from outside
    :return:
    """
    try:
        if x_requestid is None:
            raise Exception('Unique order id is None.')
        if order_name_json is None:
            raise Exception('Order name to create is None.')
        # Getting order to create from json data
        body = JSONDatagetter().get_json_order(order_name_json, x_requestid)
        # Sending message to RabbitMQ queue Ordering
        rabbit_mq_publish(os.getenv('CREATE_ORDER_ROUTING_KEY'), body)
        return True
    except Exception as e:
        raise e


def confirm_stock(order_id, x_requestid=None):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: confirm_stock
    Description: Function of Catalog simulator.
                 1.Sends message to RabbitMQ queue Ordering that items in stock
                 P.S:
                 It is response message for request of Ordering service to check items in stock.
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    body = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": "2023-03-05T14:52:24.705823Z"
    }
    rabbit_mq_publish(os.getenv('CONFIRM_STOCK_ROUTING_KEY'), body)
    return True


def reject_stock(order_id, x_requestid=None):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: reject_stock
    Description: Function of Catalog simulator.
                 1.Sends message to RabbitMQ queue Ordering that items not in stock
                 P.S:
                 It is response message for request of Ordering service to check items in stock.
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    body = {
        "OrderId": order_id,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": x_requestid,
        "CreationDate": "2023-03-05T15:51:11.5458796Z"
    }
    rabbit_mq_publish(os.getenv('REJECT_STOCK_ROUTING_KEY'), body)
    return True


def payment_succeeded(order_id, x_requestid=None):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: payment_succeeded
    Description: Function of Payment simulator.
                 1.Sends message to RabbitMQ queue Ordering that order payment succeeded.
                 P.S:
                 It is response message for request of Ordering service to order payment.
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    body = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": "2023-03-05T15:33:18.1376971Z"
    }
    rabbit_mq_publish(os.getenv('PAYMENT_SUCCEEDED_ROUTING_KEY'), body)


def payment_failed(order_id, x_requestid=None):
    """
    Name: Artsyom Sharametsieu
    Date: 05.03.2023
    Function Name: payment_succeeded
    Description: Function of Payment simulator.
                 1.Sends message to RabbitMQ queue Ordering that order payment failed.
                 P.S:
                 It is response message for request of Ordering service to order payment.
    :param order_id: autoincremented order id in db
    :param x_requestid: unique id of order generated from outside
    :return: True
    """
    body = {
        "OrderId": order_id,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": x_requestid,
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    rabbit_mq_publish(os.getenv('PAYMENT_FAILED_ROUTING_KEY'), body)


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
    order_unique_id = str(uuid.uuid4())
    create_order(order_unique_id, 'alice_order_empty_list')
