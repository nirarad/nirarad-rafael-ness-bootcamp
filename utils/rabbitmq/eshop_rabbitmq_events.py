import json
import uuid
import datetime
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from datetime import datetime, timezone
from tests.env import users_path


def rabbit_mq_publish(routing_key,body):
    with RabbitMQ() as mq:
        mq.connect()
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))

def create_order_by_user(user_name):
    with open(users_path) as f:
        users = json.load(f)
        return users[user_name]




def create_order(user_name):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    user_data = create_order_by_user(user_name)
    body = {

        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "980167ec-53b1-4cf0-9f42-7bc0d748882f",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 2,
                    "ProductName": ".NET Black & White Mug",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 1,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": formatted_time
    }
    body.update(user_data)
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent',body)

def create_order_empty_list(user_name):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    user_data = create_order_by_user(user_name)
    body = {
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "980167ec-53b1-4cf0-9f42-7bc0d748882f",
            "Items": [
                {
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": formatted_time
    }
    body.update(user_data)
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent',body)

def create_order_0_quantity(user_name):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    user_data = create_order_by_user(user_name)
    body = {
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "980167ec-53b1-4cf0-9f42-7bc0d748882f",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 2,
                    "ProductName": ".NET Black & White Mug",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 0,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": formatted_time
    }
    body.update(user_data)
    rabbit_mq_publish('UserCheckoutAcceptedIntegrationEvent',body)

def confirm_stock(order_id):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    body = {
          "OrderId": order_id,
          "Id": str(uuid.uuid4()),
          "CreationDate": formatted_time
        }
    rabbit_mq_publish('OrderStockConfirmedIntegrationEvent',body)

def reject_stock(order_id):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    body ={
        "OrderId": order_id,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": formatted_time
    }
    rabbit_mq_publish('OrderStockRejectedIntegrationEvent',body)

def payment_succeeded(order_id):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    body = {
          "OrderId": order_id,
          "Id": str(uuid.uuid4()),
          "CreationDate": formatted_time
        }
    rabbit_mq_publish('OrderPaymentSucceededIntegrationEvent', body)

def payment_failed(order_id):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    body = {
          "OrderId": order_id,
          "OrderStatus": "stockconfirmed",
          "BuyerName": "alice",
          "Id": str(uuid.uuid4()),
          "CreationDate": formatted_time
        }
    rabbit_mq_publish('OrderPaymentFailedIntegrationEvent', body)






if __name__ == '__main__':
    create_order("bob")







