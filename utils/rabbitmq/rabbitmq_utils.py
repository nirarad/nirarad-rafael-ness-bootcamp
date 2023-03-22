import json
from threading import Thread

from utils.rabbitmq.rabbitmq_send import RabbitMQ


class SingleMessageConsumer:
    def __init__(self, queue):
        self.queue = queue
        self.mq = RabbitMQ()
        self.last_msg_method = None
        self.last_msg_body = None

    # def wait_for_message(self):
    #     self.last_msg_method = None
    #     self.last_msg_body = None
    #     self.mq.connect()
    #     self.mq.consume(self.queue, self.on_message)

    def wait_for_message(self):
        self.last_msg_method = None
        self.last_msg_body = None
        self.mq.connect()
        t = Thread(target=self.mq.consume, args=[self.queue, self.on_message])
        t.start()
        t.join(timeout=5 * 60)
        if t.is_alive():
            self.mq.close()
            raise TimeoutError

    def on_message(self, ch, method, properties, body):
        self.last_msg_method = method  # Contains routing key
        self.last_msg_body = json.loads(body)
        self.mq.close()
