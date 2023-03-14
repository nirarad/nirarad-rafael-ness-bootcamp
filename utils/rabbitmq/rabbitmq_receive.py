import json
import time
import uuid

from utils.rabbitmq.rabbitmq_send import RabbitMQ
rk = ''


def callback(ch, method, properties, body):
    global rk
    rk = ''
    rk = method.routing_key
    if rk != '':
        ch.stop_consuming()


def return_glob():
    return rk


if __name__ == '__main__':
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

