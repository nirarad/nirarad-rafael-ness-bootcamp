from utils.rabbitmq.rabbitmq_send import RabbitMQ

to_print =""

def callback(ch, method, properties, body):

    global to_print
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    to_print = method.routing_key
    if to_print != None:
        ch.stop_consuming()
        print(to_print)

def routing_key():
    key = to_print
    return key





if __name__ == '__main__':
    #  with RabbitMQ() as mq:
    # #     mq.consume('Basket', callback)
    pass


