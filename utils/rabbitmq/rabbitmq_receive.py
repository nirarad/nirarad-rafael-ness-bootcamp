from utils.rabbitmq.rabbitmq_send import RabbitMQ
import threading


def callback(ch, method, properties, body):
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")


if __name__ == '__main__':
    with RabbitMQ() as mq:
        mq.consume('Ordering', callback)
        #thread = threading.Thread(target=mq.consume('Basket', callback), args=(callback))
