from utils.rabbitmq.rabbitmq_send import RabbitMQ


def callback(ch, method, properties, body):
    # print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    print(body)


if __name__ == '__main__':
    # with RabbitMQ() as mq:
    #     print(mq.consume('Ordering', callback))

    mq = RabbitMQ()
    mq.connect()
    print(mq.consume('Payment', callback))

