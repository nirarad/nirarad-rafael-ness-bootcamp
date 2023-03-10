import os
import uuid


class MessageGenerator:

    def __init__(self):
        self.user_id = os.environ["ALICE_IDENTITY"]
        self.input_request_id = str(uuid.uuid4())
        self.output_request_id = str(uuid.uuid4())
        self.current_date = "2023-03-05T13:43:13.8898923Z"
        self.basket_id = str(uuid.uuid4())

    def basket_to_order(self):
        """
        Method to generate order details.

            :return: The message that enters to the order queue, and the message that enters to the basket queue.
        """

        return {"input": {
            "UserId": self.user_id,
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
            "RequestId": self.input_request_id,
            "Basket": {
                "BuyerId": self.user_id,
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
            "CreationDate": self.current_date
        },
            "output": {
                "UserId": self.user_id,
                "Id": self.output_request_id,
                "CreationDate": self.current_date
            }
        }

    def catalog_to_order(self):
        pass