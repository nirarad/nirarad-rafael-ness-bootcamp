import json
import uuid
import os
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.testcase.jsondatagetter import JSONDatagetter
from dotenv import load_dotenv

load_dotenv('../../tests/DATA/.env.test')
Data = JSONDatagetter()


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
    # body = {
    #     "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
    #     "UserName": "alice",
    #     "OrderNumber": 0,
    #     "City": "Redmond",
    #     "Street": "15703 NE 61st Ct",
    #     "State": "WA",
    #     "Country": "U.S.",
    #     "ZipCode": "98052",
    #     "CardNumber": "4012888888881881",
    #     "CardHolderName": "Alice Smith",
    #     "CardExpiration": "2024-12-31T22:00:00Z",
    #     "CardSecurityNumber": "123",
    #     "CardTypeId": 1,
    #     "Buyer": None,
    #     "RequestId": str(uuid.uuid4()),
    #     "Basket": {
    #         "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
    #         "Items": [
    #             {
    #                 "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
    #                 "ProductId": 1,
    #                 "ProductName": ".NET Bot Black Hoodie",
    #                 "UnitPrice": 19.5,
    #                 "OldUnitPrice": 0,
    #                 "Quantity": 1,
    #                 "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
    #             }
    #         ]
    #     },
    #     "Id": str(uuid.uuid4()),
    #     "CreationDate": "2023-03-04T14:20:24.4730559Z"
    # }
    # rabbit_mq_publish(os.getenv('CREATE_ORDER_ROUTING_KEY'), body)
    try:
        if x_requestid is None:
            raise Exception('Unique order id is None.')
        if order_name_json is None:
            raise Exception('Order name to create is None.')
        # Getting order to create from json data
        body = Data.get_json_order(order_name_json, x_requestid)
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
    create_order(order_unique_id, 'alice_normal_order')
