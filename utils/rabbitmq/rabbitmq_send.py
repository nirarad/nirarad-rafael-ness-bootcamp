import pprint

import pika
import uuid
import json
# To test RabbitMQ use the following command:
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management

class RabbitMQ:
    def __init__(self, host='localhost'):
        self.connection = None
        self.channel = None
        self.host = host

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    # Connect to rabbitMq
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue)

    def close(self):
        self.connection.close()

    def publish(self, exchange, routing_key, body):
        import pprint
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        pprint.pprint(f"[{routing_key}] Sent '{body}'")

    # listening to queue until the message received
    def consume(self, queue, callback):

        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    # Clean rabbitMQ messages
    def purge(self,queue):
        self.channel.queue_purge(queue=queue)

    def clean_rabbit_messages(self):
        '''
          Writer:Romi Segal
          Date:14/03/23
          function that cleans up all the rabbit stacked messages
          :param :None
          :return: None
        '''
        self.purge('Basket')
        self.purge('Catalog')
        self.purge('Payment')
        self.purge('BackgroundTasks')
        self.purge('Ordering')

if __name__ == '__main__':
    with RabbitMQ() as mq:
        mq.purge('Catalog')
