import time
from data import config

from utils.rabbitmq.rabbitmq_send import RabbitMQ


def clear_all_queues_msg():
    print(config.queues)
    rbtMQ = RabbitMQ()
    for k, v in config.queues.items():
        rbtMQ.delete_msg_on_queue(v)
        print(v)
    time.sleep(3)
