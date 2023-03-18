import json
from utils.rabbitmq.rabbitmq_send import RabbitMQ
import uuid




class Inputs:



    def create_new_order(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))



    def create_new_order_out_of_stock(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
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
                        "Quantity": 9999,
                        "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                    }
                ]
            },
            "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
            "CreationDate": "2023-03-04T14:20:24.4730559Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def catalog_confirm(self, order_id):
        data = {"OrderId": order_id,
                "Id": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "CreationDate": "2023-03-07T09:52:56.6412897Z"}
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(data))

    def catalog_reject(self, order_id):
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

    def payment_confirm(self, order_id):
        data = {
            "OrderId": order_id,
            "Id": "b84dc7a5-1d0e-429e-a800-d3024d9c724f",
            "CreationDate": "2023-03-05T15:33:18.1376971Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentSucceededIntegrationEvent',
                       body=json.dumps(data))

    def payment_reject(self, order_id):
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

    def create_new_order_card_number_only_chars(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "errorrrrrrrrrrrrrr",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 1,
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_new_order_card_expired(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "4012888888881881",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2010-10-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 1,
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_new_order_when_CardTypeId_only_chars(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "4012888888881881",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 'error',
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_new_order_when_CardSecuirtyNumber_only_chars(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "4012888888881881",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "error",
            "CardTypeId": 1,
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_order_when_cardTypeId_not_defind(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "4012888888881881",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 9,
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_new_order_with_negative_items_quantity(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
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
                        "Quantity": -5,
                        "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                    }
                ]
            },
            "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
            "CreationDate": "2023-03-04T14:20:24.4730559Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_new_order_with_zero_items(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
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
            "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
            "CreationDate": "2023-03-04T14:20:24.4730559Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_order_when_user_not_exist_in_db(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042817",
            "UserName": "error",
            "OrderNumber": 5,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "98052",
            "CardNumber": "4012888888881881",
            "CardHolderName": "error error",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 1,
            "Buyer": "null",
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042817",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def create_order_without_zipcode(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 0,
            "City": "Redmond",
            "Street": "15703 NE 61st Ct",
            "State": "WA",
            "Country": "U.S.",
            "ZipCode": "",
            "CardNumber": "4012888888881881",
            "CardHolderName": "Alice Smith",
            "CardExpiration": "2024-12-31T22:00:00Z",
            "CardSecurityNumber": "123",
            "CardTypeId": 1,
            "Buyer": "null",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_new_order_with_productId_not_exist(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "Items": [
                    {
                        "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                        "ProductId": 999,
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_new_order_with_productId_only_chars(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "Items": [
                    {
                        "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                        "ProductId": "error",
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_new_order_with_negative_productId(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "Items": [
                    {
                        "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                        "ProductId": -2323,
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
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))

    def test_create_new_order_with_negative_price(self):
        data = {
            "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "UserName": "alice",
            "OrderNumber": 5,
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
            "Buyer": "null",
            "RequestId": str(uuid.uuid4()),
            "Basket": {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "Items": [
                    {
                        "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                        "ProductId": 1,
                        "ProductName": ".NET Bot Black Hoodie",
                        "UnitPrice": -19.5,
                        "OldUnitPrice": 0,
                        "Quantity": 1,
                        "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                    }
                ]
            },
            "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
            "CreationDate": "2023-03-04T14:20:24.4730559Z"
        }
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(data))
