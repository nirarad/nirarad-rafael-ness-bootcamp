import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ

def rabbitmq_publish(routing_key, body):
    '''
    name: Romi Segal
    date: 09/03/23
    The function publish new message on rabbitmq
    param routing_key, body
    return:
    '''
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))

def create_new_order():
    '''
    name: Romi Segal
    date: 09/03/23
    The function create new order by the user 'Alice' on rabbit
    param: none
    return: none
    '''
    body = {
        "UserId": "b74f3ddc-acae-40aa-bdab-b8ae720d7662",
        "UserName": "alice",
        "OrderNumber": 0,
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
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbitmq_publish('UserCheckoutAcceptedIntegrationEvent', body)

def create_new_order_bob():
    '''
    name: Romi Segal
    date: 09/03/23
    The function create new order on rabbit
    :param
    :return:
    '''
    body = {
        "UserId": "c208bb53-da69-42d8-a78b-fd94f4a93362",
        "UserName": "bob",
        "OrderNumber": 0,
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
            "BuyerId": "c93e9a64-e4ee-42dc-a4a1-934a76b0880d",
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
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }

    rabbitmq_publish('UserCheckoutAcceptedIntegrationEvent', body)

def create_order_without_items():
    '''
    name: Romi Segal
    date: 09/03/23
    The function create new order without items on rabbit
    param
    return:
    '''
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": 0,
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
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbitmq_publish('UserCheckoutAcceptedIntegrationEvent', body)

def create_order_quantity_0():
    '''
    name: Romi Segal
    date: 09/03/23
    The function create new order with quantity = 0
    param
    return:
    '''
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": 0,
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
                    "Quantity": 0,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbitmq_publish('UserCheckoutAcceptedIntegrationEvent', body)

def order_stock_confirmed(order_id):
    '''
    name: Romi Segal
    date: 09/03/23
    The function publish confirm_stock message
    param: order_id
    return:
    '''
    body = {
        "OrderId": order_id,
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T14:52:24.705823Z"
    }
    rabbitmq_publish('OrderStockConfirmedIntegrationEvent', body)

def order_stock_reject(order_id):
    '''
    name: Romi Segal
    date: 09/03/23
    The function publish reject_stock when there are not enough items in stock
    param:order_id
    return:
    '''
    body = {
        "OrderId": order_id,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T15:51:11.5458796Z"
    }
    rabbitmq_publish('OrderStockRejectedIntegrationEvent', body)

def order_payment_succeeded(order_id):
    '''
    name: Romi Segal
    date: 09/03/23
    The function publish payment succeeded
    param:order_id
    return:
    '''
    body = {
        "OrderId": order_id,
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T15:33:18.1376971Z"
    }
    rabbitmq_publish('OrderPaymentSucceededIntegrationEvent', body)

def payment_failed(order_id):
    '''
    name: Romi Segal
    date: 09/03/23
    The function publish payment failed
    param:order_id
    return:
    '''

    body = {
        "OrderId": order_id,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    rabbitmq_publish('OrderPaymentFailedIntegrationEvent', body)

if __name__ == '__main__':
    # create_new_order()
    create_order_without_items()
    create_order_quantity_0()

