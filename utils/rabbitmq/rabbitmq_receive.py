from utils.rabbitmq.rabbitmq_send import RabbitMQ

def callback(ch, method, properties, body):
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")


if __name__ == '__main__':
    with RabbitMQ() as mq:
        for i in range (100):
         mq.consume('Ordering', callback())
