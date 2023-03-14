import pika
import uuid
import json


# To test RabbitMQ use the following command:
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management


class RabbitMQ:
    def __init__(self, host='localhost'):
        self.connection = None
        self.channel = None
        self.host = host

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue)

    def close(self):
        self.connection.close()

    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        print(f"[{routing_key}] Sent '{body}'")

    def consume(self, queue, callback):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()


if __name__ == '__main__':
    input_massage1_test4 = {
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
        "Id": "16c5ddbc-229e-4c19-a4bd-d4148417529c",
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }

    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key='UserCheckoutAcceptedIntegrationEvent',
                   body=json.dumps(input_massage1_test4))