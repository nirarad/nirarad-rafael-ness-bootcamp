import json
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from datetime import datetime


def rabbit_mq_publish(routing_key, body):
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))


def current_time():
    return datetime.utcnow().isoformat()

