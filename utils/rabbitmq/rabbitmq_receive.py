from rabbitmq_send import RabbitMQ


def callback(ch, method, properties, body):
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    ch.stop_consuming()
       
if __name__ == '__main__':
    with RabbitMQ() as mq:
        mq.consume('Ordering', callback)
        
        
        





     
