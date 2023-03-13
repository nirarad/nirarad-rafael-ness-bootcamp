import time

from utils.rabbitmq.eshop_rabbitmq_events import payment_succeeded, payment_failed
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


def callback(ch, method, properties, body):
    # print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    # dict_body = eval(body)
    # print(dict_body)
    # print("\n")
    # print(dict_body['OrderId'])
    # print(type(dict_body['OrderId']))
    # print("\n")
    # print(dict_body['Id'])
    # print(type(dict_body['Id']))
    # print("\n")
    # print(dict_body['CreationDate'])
    # print(type(dict_body['CreationDate']))
    # payment_succeeded(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
    payment_succeeded('319', 'f302f5a8-522a-409f-b4dd-76f9cfb7aa5e', '2023-03-13T15:43:29.2988114Z')


def consume():
    start_time = time.time()
    with RabbitMQ() as mq:
        mq.consume('Payment', callback)
        # mq.channel.
        # print(callback_body)
        # while True:
        #     if time.time() - start_time < 10:
        #         pass
        #     # if 10 sec pass no sense to wait
        #     elif time.time() - start_time > 10:  # Timeout after 10 seconds
        #         return False
        #     # Updating time
        #     time.sleep(0.1)


if __name__ == '__main__':
    callback(0, 0, 0, 0)
