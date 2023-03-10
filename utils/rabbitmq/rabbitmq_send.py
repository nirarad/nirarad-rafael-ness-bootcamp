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
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue)

    def close(self):
        self.connection.close()

    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
        print(f"[{routing_key}] Sent '{body}'")

    def consume(self, queue):
        self.channel.basic_consume(queue=queue, on_message_callback=self.add_message_to_list, auto_ack=True)
        self.channel.start_consuming()

    def add_message_to_list(self, ch, method, properties, body):
        self.waiting_messages.append(body)
        pprint.pprint(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")

    def purge_queue(self, queue_name):
        self.channel.queue_purge(queue_name)

    # def get_first_message(self, message_number, queue_name):
    #     for i in range(2):
    #         try:
    #             method_frame, header_frame, body = self.channel.basic_get(queue_name, auto_ack=True)
    #         except ValueError as v:
    #             raise ValueError(f'There was problem with getting the {message_number} message, the following exception was received: {v}')
    #         print(body)
    #         if i + 1 == message_number:
    #             return body
    #
    def read_first_message(self, queue_name):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue_name, auto_ack=True)
            return body
        except ValueError as v:
            raise ValueError(
                f'There was problem with getting the first message, the following exception was received: {v}')

# if __name__ == '__main__':
#     bodys = {
#         "OrderId": 1,
#         "Id": str(uuid.uuid4()),
#         "CreationDate": "2023-03-05T15:33:18.1376971Z"
#     }
#     with RabbitMQ() as mq:
#         mq.publish(exchange='eshop_event_bus',
#                    routing_key='OrderPaymentSucceededIntegrationEvent',
#                    body=json.dumps(bodys))
