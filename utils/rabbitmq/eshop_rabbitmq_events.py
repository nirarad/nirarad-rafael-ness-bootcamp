import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def create_order(x_requestid=None, order_number=0):
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": order_number,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 1,
                    "ProductName": ".NET Bot Black Hoodie",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 1,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": x_requestid,
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent', body)
    return True


def create_order_empty_list(order_number=0, x_requestid=None):
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": order_number,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                }
            ]
        },
        "Id": x_requestid,
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent', body)


def create_order_0_quantity(x_requestid=None, order_number=0):
    uuids = str(uuid.uuid4())
    print('\n', uuids)
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": order_number,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": uuids,
        "Basket": {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 1,
                    "ProductName": ".NET Bot Black Hoodie",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 0,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": x_requestid,
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent', body)


def confirm_stock(order_id, x_requestid=None):
    body = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": "2023-03-05T14:52:24.705823Z"
    }
    rabbit_mq_publish('OrderStockConfirmedIntegrationEvent', body)


def reject_stock(order_id, x_requestid=None):
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
    rabbit_mq_publish('OrderStockRejectedIntegrationEvent', body)


def change_status_awaiting_validation(x_requestid=None, order_number=0):
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
        "Id": x_requestid,
        "CreationDate": "2023-03-05T14:27:28.8042812Z"
    }
    rabbit_mq_publish('OrderStatusChangedToAwaitingValidationIntegrationEvent', body)


def payment_succeeded(order_id, x_requestid=None):
    body = {
        "OrderId": order_id,
        "Id": x_requestid,
        "CreationDate": "2023-03-05T15:33:18.1376971Z"
    }
    rabbit_mq_publish('OrderPaymentSucceededIntegrationEven', body)


def payment_failed(order_id, x_requestid=None):
    body = {
        "OrderId": order_id,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": x_requestid,
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    rabbit_mq_publish('OrderPaymentFailedIntegrationEvent', body)


if __name__ == '__main__':
    create_order()
