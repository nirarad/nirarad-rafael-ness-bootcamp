import pika


class RabbitMQ:
    def __init__(self, host='localhost'):
        self.connection = None
        self.channel = None
        self.host = host
        self.rout_key = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue)

    def close(self):
        if self.connection:
            self.connection.close()

    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        print(f"[{routing_key}] Sent '{body}'")

    def purge(self, queue):
        self.channel.queue_purge(queue=queue)

    def purge_all(self):
        queues = ['Basket', 'Catalog', 'Ordering', 'Ordering.signalrhub', 'Payment', 'Webhooks']
        for queue in queues:
            self.channel.queue_purge(queue)

    def callback(self, ch, method, properties, body):
        self.rout_key = method.routing_key
        if self.rout_key:
            ch.stop_consuming()

    def get_routing_key(self, queue):
        self.consume(queue, self.callback)
        return self.rout_key

    def consume(self, queue, callback):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()


if __name__ == '__main__':
    # body = {
    #    "OrderId": 1,
    #    "Id": str(uuid.uuid4()),
    #    "CreationDate": "2023-03-05T15:33:18.1376971Z"
    # }
    # with RabbitMQ() as mq:
    #    mq.publish(exchange='eshop_event_bus',
    #               routing_key='OrderPaymentSucceededIntegrationEvent',
    #               body=json.dumps(body))

    with RabbitMQ() as mq:
        mq.purge_all()
