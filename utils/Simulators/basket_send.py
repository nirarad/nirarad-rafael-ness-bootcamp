import unittest
from utils.docker.docker_utils import *
from utils.MyFunctions import *
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.db.db_utils import *
import uuid
import json
import datetime
class Basket_send:

    def __init__(self, count_items, user: str):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        currrent_time = datetime.datetime.now().strftime("%H:%M:%S")
        body = {
              "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
              "UserName": user.lower(),
              "OrderNumber": 0,
              "City": "Redmond",
              "Street": "15703 NE 61st Ct",
              "State": "WA",
              "Country": "U.S.",
              "ZipCode": "98052",
              "CardNumber": "4012888888881881",
              "CardHolderName": f"{user} Smith",
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
                    "Quantity": count_items,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                  }
                ]
              },
              "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
              "CreationDate": f"{today}T{currrent_time}.4730559Z"
            }

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))