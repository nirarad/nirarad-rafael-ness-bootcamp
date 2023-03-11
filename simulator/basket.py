import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def create_order(order_number):
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
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent', body)


def output_remove_items():
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T13:43:13.8898923Z"
    }

    return body

if __name__ == '__main__':
    create_order(7)
