from utils.rabbitmq.rabbitmq_send import RabbitMQ


def Receive_message_from_queue(queue):
    with RabbitMQ() as mq:
        return mq.get_routing_key(queue)


if __name__ == '__main__':
    with RabbitMQ() as mq:
        routing_key = mq.get_routing_key('Ordering.signalrhub')
        print(routing_key)
