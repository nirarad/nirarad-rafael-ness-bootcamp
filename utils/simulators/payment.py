import json
import time
import uuid

from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ


def callback(ch, method, properties, body):
    #  log it ..
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")


class Payment(object):
    def __init__(self, rbt_send: RabbitMQ, log: Exceptions_logs):
        self.rbtMQ = rbt_send
        self.log = log
        self.routing_key_payment_get = None
        self.count = 50

    def send_to_queue(self, routing_key, order_id):
        body = {
            "OrderId": order_id,
            "Id": "b84dc7a5-1d0e-429e-a800-d3024d9c724f",
            "CreationDate": "2023-03-05T15:33:18.1376971Z"
        }

        with self.rbtMQ as send:
            send.publish(exchange='eshop_event_bus',
                         routing_key=routing_key,
                         body=json.dumps(body))

    def consume(self):
        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Payment\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")

            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_payment_get = method.routing_key
                ch.stop_consuming()

            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue='Payment', callback=callback)
