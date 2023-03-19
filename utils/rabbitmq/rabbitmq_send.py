import pika
import uuid


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

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue, durable=True)

    def close(self):
        self.connection.close()

    def purge_queue(self):
        """
        Method to purge the given queue.
        """
        try:
            with RabbitMQ() as mq:
                mq.purge_queue(self.queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def purge(self, queue):
        self.channel.queue_purge(queue=queue)

    def clean_rabbit_messages(self):
        """
          Writer: chani kadosh
          Date:14/03/23
          function that cleans up all the rabbit stacked messages
        """
        self.purge('Basket')
        self.purge('Catalog')
        self.purge('Payment')
        self.purge('BackgroundTasks')
        self.purge('Ordering')



    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        print(f"[{routing_key}] Sent '{body}'")

    def consume(self, queue, callback):
            self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            self.channel.start_consuming()


if __name__ == '__main__':

    with RabbitMQ() as mq:
        pass
        # mq.publish(exchange='eshop_event_bus',
        #            routing_key='UserCheckoutAcceptedIntegrationEvent',
        #            body=json.dumps(body))
        # mq.connect()
        # time.sleep(300)
        # mq.read_first_message('Ordering')
        # mq.declare_queue1("Payment", durable=False)
        # print(mq.queues_list())
        # print(mq.purge_all_queues(mq.queues_list()))
        # mq.purge_queuep('Catalog')

