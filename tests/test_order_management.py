import datetime
import json
import uuid

import pytest

from simulators.basket_simulator import BasketSimulator

pytest.mark.parametrize()


def test_main_success_scenario():
    # data settings
    request_id = str(uuid.uuid4())
    current_date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    input_1 = {
        "UserId": "5b2eb009-f2b4-4406-a2a5-2949721f7872",
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
        "RequestId": request_id,
        "Basket": {
            "BuyerId": "5b2eb009-f2b4-4406-a2a5-2949721f7872",
            "Items": [
                {
                    "Id": "ec13598b-9a25-4624-b0a0-e9069be548d2",
                    "ProductId": 1,
                    "ProductName": ".NET Bot Black Hoodie",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 1,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                },
                {
                    "Id": "43b0d9d0-802b-4987-b9a1-b648b094f5d3",
                    "ProductId": 6,
                    "ProductName": ".NET Blue Hoodie",
                    "UnitPrice": 12,
                    "OldUnitPrice": 0,
                    "Quantity": 1,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/6/pic/"
                },
                {
                    "Id": "1c82cfd8-099b-4ea2-854f-7ee287684a08",
                    "ProductId": 2,
                    "ProductName": ".NET Black \u0026 White Mug",
                    "UnitPrice": 8.5,
                    "OldUnitPrice": 0,
                    "Quantity": 1,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/2/pic/"
                }
            ]
        },
        "Id": request_id,
        "CreationDate": current_date
    }
    output_1 = {
        "UserId": request_id,
        "Id": request_id,
        "CreationDate": "2023-03-05T13:43:13.8898923Z"
    }

    output_2 = {
        "UserId": request_id,
        "Id": request_id,
        "CreationDate": "2023-03-05T13:43:13.8898923Z"
    }

    # step 1
    with BasketSimulator(json.dumps(input_1)) as bm:
        bm.accept_user_checkout()
        # bm.start_consume_for_order_integration_message()

        message_to_check = bm.read_n_messages(1)
        assert message_to_check == json.dumps(output_2)
