import json
import pprint

import pika


# To test RabbitMQ use the following command:
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management


class RabbitMQ:
    def __init__(self, host='localhost'):
        self.connection = None
        self.channel = None
        self.host = host
        self.waiting_messages = []

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue)

    def close(self):
        self.connection.close()

    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)

    def consume(self, queue):
        self.channel.basic_consume(queue=queue, on_message_callback=self.add_message_to_list, auto_ack=True)
        self.channel.start_consuming()

    def add_message_to_list(self, ch, method, properties, body):
        self.waiting_messages.append(body)
        pprint.pprint(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")

    def purge_queue(self, queue_name):
        self.channel.queue_purge(queue_name)

    def get_all_queues_names(self):
        queues = []
        for queue in self.channel.get_queue(''):
            queues.append(queue.method)
        return queues

    def read_first_message(self, queue_name):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue_name, auto_ack=True)
            if method_frame:
                self.channel.basic_ack(method_frame.delivery_tag)
                return json.loads(body.decode('utf-8'))
            else:
                raise TimeoutError
        except ValueError as v:
            raise ValueError(
                f'There was a problem with getting the first message, the following exception was received: {v}')

    def get_number_of_messages_in_queue(self, queue_name):
        try:
            queue = self.channel.get_queue(queue_name)

            # Return the amount of messages in the queue.
            return queue.method.message_count
        except ValueError as v:
            raise ValueError(
                f'There a was problem with getting the first message from the {queue_name} queue, the following exception was received: {v}')

    def validate_queue_is_empty(self, queue_name):
        try:
            queue = self.channel.queue_declare(queue_name, durable=True)
            # Validate that the queue is empty.
            counter = queue.method.message_count
            while counter > 0:
                counter = queue.method.message_count
            else:
                return True
        except ValueError as v:
            raise ValueError(
                f'There was a problem with getting the first message from the {queue_name} queue, the following exception was received: {v}')
