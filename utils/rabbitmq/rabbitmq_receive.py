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





if __name__ == '__main__':
    #  with RabbitMQ() as mq:
    # #     mq.consume('Basket', callback)
    pass


