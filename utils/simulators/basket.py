import time

import dotenv

from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ
import uuid
import json


class Basket(object):
    def __init__(self, rbt_send: RabbitMQ, log: Exceptions_logs):
        self.rbtMQ = rbt_send
        self.log = log
        self.routing_key_basket_get = None
        self.count = 50
        self.config = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../../.env"))
        self.body = json.load(open(self.config["BODY"]))
        self.exch = json.load(open(self.config["EXCH"]))

    def send_to_queue(self, routing_key):
        self.body["basket"]["RequestId"] = str(uuid.uuid4())
        body = self.body["basket"]
        with self.rbtMQ as send:
            send.publish(exchange=self.exch["exchange"],
                         routing_key=routing_key,
                         body=json.dumps(body))

    def consume(self):
        """
        Name: Menahem Rotblat.\n
        Description: consuming with rabbitMQ consume method by callback function,
        when getting a message, consuming stops.\n
        Date: 16/03/23
        """

        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Basket\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_basket_get = method.routing_key
                ch.stop_consuming()
                # self.rbtMQ.close()

            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue='Basket', callback=callback)
