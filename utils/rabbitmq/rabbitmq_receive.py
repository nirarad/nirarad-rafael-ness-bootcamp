#TODO
# on callback: check if the relevant routing key are coming and
import json
from pprint import pprint

from utils.rabbitmq.rabbitmq_send import RabbitMQ


def callback(ch, method, properties, body):
    # pprint(str(body).find("routing_key",0,len(body)))
    pprint(f"[{ch}]\n Method: {method},\n\n Properties: {properties},\n\n Body: {body}")


if __name__ == '__main__':
    with RabbitMQ() as mq:
        if mq.connection is None:
            pprint("no connecting, try to restart")
            mq.connect()
        mq.consume('Basket', callback)
