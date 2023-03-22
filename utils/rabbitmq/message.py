import json
from utils.rabbitmq.rabbitmq_send import RabbitMQ
import uuid
from datetime import datetime


class Message:
    def order_data(self, user_id: str = 'b9e5dcdd-dae2-4b1c-a991-f74aae042814', username: str = "alice",
                   order_number: int = 0, city: str = "Redmond", street: str = "15703 NE 61st Ct",
                   state: str = "WA", country: str = "U.S.", zip_code: str = "98052", card_type_id: int = 1,
                   card_holder_name: str = "Alice Smith",
                   buyer_id: str = "b9e5dcdd-dae2-4b1c-a991-f74aae042814", product_id: int = 1,
                   product_name: str = ".NET Bot Black Hoodie", unit_price: float = 19.5, quantity: int = 1,
                   card_number: str = "4012888888881881", card_security_number: str = "123",
                   item_id: str = "c1f98125-a109-4840-a751-c12a77f58dff",
                   card_expiration="2024-12-31T22:00:00Z"):
        data = {
            "UserId": user_id,
            "UserName": username,
            "OrderNumber": order_number,
            "City": city,
            "Street": street,
            "State": state,
            "Country": country,
            "ZipCode": zip_code,
            "CardNumber": card_number,
            "CardHolderName": card_holder_name,
            "CardExpiration": card_expiration,
            "CardSecurityNumber": card_security_number,
            "CardTypeId": card_type_id,
            "Buyer": buyer_id,
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": buyer_id,
                "Items": [
                    {
                        "Id": item_id,
                        "ProductId": product_id,
                        "ProductName": product_name,
                        "UnitPrice": unit_price,
                        "OldUnitPrice": 0,
                        "Quantity": quantity,
                        "PictureUrl": f"http://host.docker.internal:5202/c/api/v1/catalog/items/{product_id}/pic/"
                    }
                ]
            },
            "Id": str(uuid.uuid4()),
            "CreationDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def catalog_input_confirmed(self, order_id):
        data = {"OrderId": order_id,
                "Id": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "CreationDate": "2023-03-07T09:52:56.6412897Z"}
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(data))

    def catalog_input_Rejected(self, order_id):
        data = {
            "OrderId": order_id,
            "OrderStockItems": [
                {
                    "ProductId": 1,
                    "HasStock": False
                }
            ],
            "Id": "99c3f974-c6ed-41a4-8e01-5cb00f9e6335",
            "CreationDate": "2023-03-05T15:51:11.5458796Z"
        }

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockRejectedIntegrationEvent',
                       body=json.dumps(data))

    #
    def payment_input_succeed(self, order_id):
        data = {
            "OrderId": order_id,
            "Id": "b84dc7a5-1d0e-429e-a800-d3024d9c724f",
            "CreationDate": "2023-03-05T15:33:18.1376971Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentSucceededIntegrationEvent',
                       body=json.dumps(data))

    def payment_input_rejected(self, order_id):
        data = {
            "OrderId": order_id,
            "OrderStatus": "stockconfirmed",
            "BuyerName": "alice",
            "Id": "cca155c0-4480-4c93-a763-910e54218040",
            "CreationDate": "2023-03-05T17:07:35.6306122Z"
        }

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentFailedIntegrationEvent',
                       body=json.dumps(data))
