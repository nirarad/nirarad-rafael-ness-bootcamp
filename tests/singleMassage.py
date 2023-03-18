import json
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class SingleMessageConsumer:

    def __init__(self, queue):
        self.queue = queue
        self.mq = RabbitMQ()
        self.last_msg_method = None #routing key
        self.last_msg_body = None #body of the message

    # connect to rabbitMq and consuming to queue until the specific message received
    def wait_for_message(self):
        self.last_msg_method = None
        self.last_msg_body = None
        self.mq.connect()
        self.mq.consume(self.queue, self.on_message)

    # message with routing key and body
    def on_message(self, ch, method, properties, body):
        self.last_msg_method = method #routing key
        self.last_msg_body = json.loads(body) #body of the message
        self.mq.close()

