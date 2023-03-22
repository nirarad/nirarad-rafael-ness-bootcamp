import uuid as uuid

ALICE = "50f0dbf5-9b8a-4757-bee3-b1750ab447a3"
BOB = "67a8c036-5f8e-423e-9130-030dc795612e"

NAME_ALICE = 'alice'
NAME_BOB = 'bob'

PASSWORD = 'Pass123$'

CARD_TYPE = 8

USER_CHECKOUT_ACCEPTED_MESSAGE = {
    "UserId": ALICE,
    "UserName": NAME_ALICE,
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

ORDER_STOCK_CONFIRMED_MESSAGE = {
    "OrderId": 0,
    "Id": str(uuid.uuid4()),
    "CreationDate": "2023-03-07T09:52:56.6412897Z"
}

ORDER_OUT_OF_STOCK_MESSAGE = {
    "OrderId": 0,
    "OrderStockItems": [
        {
            "ProductId": 1,
            "HasStock": False
        }
    ],
    "Id": str(uuid.uuid4()),
    "CreationDate": "2023-03-04T14:20:24.4730559Z"
}

ORDER_PAYMENT_SUCCEEDED_MESSAGE = {
    "OrderId": 0,
    "Id": str(uuid.uuid4()),
}

ORDER_PAYMENT_FAILURE_MESSAGE = {
    "OrderId": 0,
    "OrderStatus": "stockconfirmed",
    "BuyerName": "alice",
    "Id": "cca155c0-4480-4c93-a763-910e54218040",
    "CreationDate": "2023-03-05T17:07:35.6306122Z"
}
