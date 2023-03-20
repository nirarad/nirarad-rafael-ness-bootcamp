from rabbitmq_send import RabbitMQ


def callback(ch, method, properties, body):
    print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
    ch.stop_consuming()

        
        





     
