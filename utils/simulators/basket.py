import time
from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ
import uuid
import json


# def callback(ch, method, properties, body):
#     #  log it ..
#     pprint(body.decode())
#     pprint(f"[{ch}]\n Method: {method},\n Properties: {properties},\n Body: {body}")
#     # ch.basic_ack(delivery_tag=method.delivery_tag)

class Basket(object):
    def __init__(self, rbt_send: RabbitMQ, log: Exceptions_logs):
        self.rbtMQ = rbt_send
        self.log = log
        self.routing_key_basket_get = None
        self.count = 50

    def send_to_queue(self, routing_key):
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
                        "Quantity": 1,
                        "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                    }
                ]
            },
            "Id": "e9b80940-c861-4e5b-9d7e-388fd256acef",
            "CreationDate": "2023-03-04T14:20:24.4730559Z"
        }

        with self.rbtMQ as send:
            send.publish(exchange='eshop_event_bus',
                         routing_key=routing_key,
                         body=json.dumps(body))

    def consume(self):

        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Basket\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")

            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_basket_get = method.routing_key
                ch.stop_consuming()

            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue='Basket', callback=callback)
