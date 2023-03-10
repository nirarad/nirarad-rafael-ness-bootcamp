import json
import uuid

from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.eshop_rabbitmq_events import *
from utils.rabbitmq.rabbitmq_receive import *


def place_order():
    create_order()


def consume():
    with RabbitMQ() as mq:
        print(mq.consume('Basket', callback))


if __name__ == '__main__':
    id = str(uuid.uuid4())
    place_order()
    consume()
