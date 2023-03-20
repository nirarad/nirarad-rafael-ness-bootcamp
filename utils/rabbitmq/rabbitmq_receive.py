import json
import pprint

from utils.rabbitmq.rabbitmq_send import RabbitMQ

if __name__ == '__main__':
    #with RabbitMQ() as mq:
    mq=RabbitMQ()
    mq.connect()
    mq.consume('Basket')
    print(mq.last_msg_body)
    print(mq.last_msg_method.routing_key)
    mq.close()



