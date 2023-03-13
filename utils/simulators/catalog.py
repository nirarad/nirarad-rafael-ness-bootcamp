import datetime
import json
import time
import uuid

from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class Catalog(object):
    def __init__(self, rbt_send: RabbitMQ, log: Exceptions_logs):
        self.rbtMQ = rbt_send
        self.log = log
        self.routing_key_catalog_get = None
        self.count = 1

    def send_to_queue(self, routing_key, order_id):
        body = {
            "OrderId": order_id,
            "Id": "e9b80940-c861-4e5b-9d7e-388fd256acef",
            "CreationDate": "2023-03-07T09:52:56.6412897Z"
        }

        with self.rbtMQ as send:
            send.publish(exchange='eshop_event_bus',
                         routing_key=routing_key,
                         body=json.dumps(body))

    def consume(self):
        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Catalog\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")

            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_catalog_get = method.routing_key
                ch.stop_consuming()
            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue='Catalog', callback=callback)
