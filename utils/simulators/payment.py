import json
import time
import uuid

import dotenv

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
        self.config = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../../.env"))
        self.queues = json.load(open(self.config["QUEUE"]))
        self.r_key = json.load(open(self.config["R_KEY"]))
        self.exch = json.load(open(self.config["EXCH"]))
        self.body_obj = json.load(open(self.config["BODY"]))

    def send_to_queue(self, routing_key, order_id):
        with self.rbtMQ as send:
            send.publish(exchange=self.exch["exchange"],
                         routing_key=routing_key,
                         body=json.dumps(self.body(routing_key, order_id)))

    def consume(self):
        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Payment\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_payment_get = method.routing_key
                ch.stop_consuming()
                # self.rbtMQ.close()
            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue=self.queues["payment"], callback=callback)
            # mq.close()

    def body(self, routing_key, order_id):
        if routing_key == self.r_key["sending"]["payment"]["succeeded"]:
            self.body_obj["payment"]["succeeded"]["OrderId"] = order_id
            self.body_obj["payment"]["succeeded"]["Id"] = str(uuid.uuid4())
            return self.body_obj["payment"]["succeeded"]
        if routing_key == self.r_key["sending"]["payment"]["failed"]:
            self.body_obj["payment"]["failed"]["OrderId"] = order_id
            self.body_obj["payment"]["failed"]["Id"] = str(uuid.uuid4())
            return self.body_obj["payment"]["failed"]
