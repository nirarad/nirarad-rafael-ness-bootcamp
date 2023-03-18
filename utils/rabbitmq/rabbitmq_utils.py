import time
from data import config

from utils.rabbitmq.rabbitmq_send import RabbitMQ


def clear_all_queues_msg():
    rbtMQ = RabbitMQ()
    for k, v in config.queues.items():
        rbtMQ.delete_msg_on_queue(v)
    time.sleep(3)
