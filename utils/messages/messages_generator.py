import uuid
from datetime import datetime

from faker import Faker

current_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")


class MessageGenerator:

    @staticmethod
    def generate_basket_to_order_message():
        """
        Static method to generate order reservation details.
        :return: The order reservation in json format
        """
        fake = Faker()
        return {
            "UserId": str(uuid.uuid4()), "UserName": fake.name(), "OrderNumber": 0, "City": fake.city(),
            "Street": fake.street_address(), "State": fake.state(), "Country": "U.S.", "ZipCode": "98052",
            "CardNumber": "4012888888881881", "CardHolderName": "Alice Smith", "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123", "CardTypeId": 1, "Buyer": None, "RequestId": str(uuid.uuid4()),
            "Basket": {"BuyerId": str(uuid.uuid4()), "Items": [
                {"Id": "ec13598b-9a25-4624-b0a0-e9069be548d2", "ProductId": 1, "ProductName": ".NET Bot Black Hoodie",
                 "UnitPrice": 19.5, "OldUnitPrice": 0, "Quantity": 1,
                 "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"},
                {"Id": "43b0d9d0-802b-4987-b9a1-b648b094f5d3", "ProductId": 6, "ProductName": ".NET Blue Hoodie",
                 "UnitPrice": 12, "OldUnitPrice": 0, "Quantity": 1,
                 "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/6/pic/"},
                {"Id": "1c82cfd8-099b-4ea2-854f-7ee287684a08", "ProductId": 2,
                 "ProductName": ".NET Black \u0026 White Mug", "UnitPrice": 8.5, "OldUnitPrice": 0, "Quantity": 1,
                 "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/2/pic/"}]}, "Id": {},
            "CreationDate": current_date
        }
