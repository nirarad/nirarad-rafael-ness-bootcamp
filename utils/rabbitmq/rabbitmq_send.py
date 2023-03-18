import json

import pika


class RabbitMQ:

    def __init__(self, host='localhost'):
        """
        RabbitMQ connector initializer.
        Parameters:
            host: The host of the RabbitMQ server.
        """
        self.connection = None
        self.channel = None
        self.host = host

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

    def purge_queue(self, queue_name):
        """
        Method to purge a given queue.
        Parameters:
            queue_name: The queue to purge.
        """
        self.channel.queue_purge(queue_name)

    def read_first_message(self, queue_name):
        """
        Method to read the first message from a given queue.
        Parameters:
            queue_name:
        Returns: The first message in the given queue.
        """
        try:
            # Get the first message.
            method_frame, header_frame, body = self.channel.basic_get(queue_name, auto_ack=True)
            if method_frame:
                # Acknowledged and return the message if exists.
                self.channel.basic_ack(method_frame.delivery_tag)
                return json.loads(body.decode('utf-8'))
            else:
                raise TimeoutError
        except ValueError as v:
            raise ValueError(
                f'There was a problem with getting the first message, the following exception was received: {v}')

    def get_number_of_messages_in_queue(self, queue_name):
        """
        Method to return the amount messages in a given queue.
        Parameters:
            queue_name:
        Returns:
            The messages amount of the given queue.
        """
        try:
            # Locate the queue.
            queue = self.channel.queue_declare(queue_name, durable=True)

            return queue.method.message_count
        except ValueError as v:
            raise ValueError(
                f'There a was problem with getting the first message from the {queue_name} queue, the following exception was received: {v}')

    def validate_queue_is_empty_once(self, queue_name):
        """
        Method to validate one time only if the queue is empty from messages.
        Parameters:
            queue_name: The given queue to check.
        Returns:
            True if the queue is empty, and False otherwise.
        """
        try:
            # Locate the queue.
            queue = self.channel.queue_declare(queue_name, durable=True)

            # Validate that the queue is empty.
            return queue.method.message_count == 0

        except ValueError as v:
            raise ValueError(
                f'There was a problem with getting the first message from the {queue_name} queue, the following exception was received: {v}')

    def clear_queue_chronologically(self, queue_name):
        """
        Method to clear the queue from messages one by one.
        Parameters:
            queue_name: The given queue to clear.
        Returns:
            True if the clearance has been done successfully.
        """
        try:
            queue = self.channel.queue_declare(queue_name, durable=True)
            current_messages_amount = queue.method.message_count

            while current_messages_amount > 0:
                # Validate that the queue is empty.
                current_messages_amount = queue.method.message_count

            return True

        except ValueError as v:
            raise ValueError(
                f'There was a problem with getting the first message from the {queue_name} queue, the following exception was received: {v}')
