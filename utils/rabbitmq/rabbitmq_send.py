import os

import pika
import uuid
import json

from dotenv import load_dotenv


# To test RabbitMQ use the following command:
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management


class RabbitMQ:
    def __init__(self, host='localhost'):
        # ENV
        load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env.test'))
        self.queues = [os.getenv('BASKET_QUEUE'), os.getenv('ORDERING_QUEUE'), os.getenv('CATALOG_QUEUE'),
                       os.getenv('PAYMENT_QUEUE')]
        self.connection = None
        self.channel = None
        self.host = host

    def __enter__(self):
        """Connecting to rabbitmq when is self instance"""
        self.connect()
        return self

    def connect(self):
        """Connecting to rabbitmq"""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        """Queue declaration to channel"""
        self.channel.queue_declare(queue=queue)

    def bind(self, queue_name, exchange_name, routing_key):
        """Binding routing key to queue"""
        self.channel.queue_bind(queue_name, exchange_name, routing_key)

    def publish(self, exchange, routing_key, body):
        """Publishing message to rabbitmq"""
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        print(f"[{routing_key}] Sent '{body}'")
        return body

    def purge(self, queue):
        """Cleaning messages in one """
        self.channel.queue_purge(queue=queue)

    def purge_all(self):
        """Cleaning messages in all queues"""
        for queue in self.queues:
            self.channel.queue_purge(queue=queue)

    def consume(self, queue, callback):
        """Get message from rabbitmq queue and invoke callback method"""
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def close(self):
        """Closing connection to rabbitmq"""
        self.connection.close()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Closing connection to rabbitmq when is self instance"""
        self.connection.close()


if __name__ == '__main__':
    # body = {
    #     "OrderId": 1,
    #     "Id": str(uuid.uuid4()),
    #     "CreationDate": "2023-03-05T15:33:18.1376971Z"
    # }
    # with RabbitMQ() as mq:
    #     mq.publish(exchange='eshop_event_bus',
    #                routing_key='OrderPaymentSucceededIntegrationEvent',
    #                body=json.dumps(body))
    #

    with RabbitMQ() as mq:
        mq.purge_all()
