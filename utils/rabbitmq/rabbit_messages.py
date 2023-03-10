import uuid
import json
import pika
from utils.db.db_utils import MSSQLConnector
class RabbitMessages:



    def usercheckout(self):
     body= {
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
                "Buyer": 'null',
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
                "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
                "CreationDate": "2023-03-04T14:20:24.4730559Z"
            }
     return body

    def stockconfirmed(self):
        body={
                "OrderId": 164,
                "Id": "e9b80940-c861-4e5b-9d7e-388fd256acef",
                "CreationDate": "2023-03-07T09:52:56.6412897Z"
             }
        return body


    def paymentsuccses(self):
        body={
                "OrderId": 164,
                "Id": "b84dc7a5-1d0e-429e-a800-d3024d9c724f",
                "CreationDate": "2023-03-05T15:33:18.1376971Z"
             }
        return body
