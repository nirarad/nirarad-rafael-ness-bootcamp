import json
import uuid

from utils.rabbitmq.rabbitmq_send import RabbitMQ

def callback(ch, method, properties, body):
    #  log it ..
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")


class Catalog(object):
    def __init__(self, rbt_send: RabbitMQ):
        self.send = rbt_send

    def send_to_queue(self, routing_key, order_id):
        body = {
            "OrderId": order_id,
            "Id": str(uuid.uuid4()),
            "CreationDate": "2023-03-05T15:33:18.1376971Z"
        }
        with self.send as send:
            send.publish(exchange='eshop_event_bus',
                         routing_key=routing_key,
                         body=json.dumps(body))

    def consume(self):
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)