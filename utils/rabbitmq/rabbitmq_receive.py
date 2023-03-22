from utils.rabbitmq.rabbitmq_send import RabbitMQ

routing =""

def callback(ch, method, properties, body):

    global routing
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    routing = method.routing_key
    if routing != None:
        ch.stop_consuming()
        print(routing)

def global_key():
    key = routing
    return key

def clear_purge():
    """
    Author: Artium Brovarnik
    Description: clear queues from messages
    date 16.3.23
    """
    with RabbitMQ() as mq:
        mq.clear_queues('Basket')
        mq.clear_queues('Catalog')
        mq.clear_queues('Payment')



if __name__ == '__main__':

    pass


