import json
import time

import dotenv

from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class Signalrhub(object):
    def __init__(self, rbt_send: RabbitMQ, log: Exceptions_logs):
        self.count = 50
        self.log = log
        self.routing_key_srh_get = None
        self.rbtMQ = rbt_send
        self.config = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../../.env"))
        self.queues = json.load(open(self.config["QUEUE"]))

    def consume(self):
        def callback(ch, method, properties, body):
            self.log.send(
                f"\n\ncomponent: Signalrhub\n\n[{ch}]\n\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}\n\n ----------------")

            if len(str(method)) > 0 or self.count == 0:
                self.routing_key_srh_get = method.routing_key
                ch.stop_consuming()

            time.sleep(1)
            self.count -= 1

        with self.rbtMQ as mq:
            mq.consume(queue=self.queues["signalrhub"], callback=callback)

