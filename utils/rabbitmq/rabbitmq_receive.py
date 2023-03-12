from utils.rabbitmq.rabbitmq_send import RabbitMQ

rk = ''


def callback(ch, method, properties, body):
    global rk
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    # ch.stop_consuming()
    rk = method.routing_key
    if rk != '':
        ch.stop_consuming()


def check_rk(routing_key):
    if rk == routing_key:
        return True
    return False


if __name__ == '__main__':
    with RabbitMQ() as mq:
        mq.consume('Catalog', callback)

    print(rk)
