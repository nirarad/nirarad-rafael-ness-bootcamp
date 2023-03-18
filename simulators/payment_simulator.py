import json
import os
import threading
import time

from dotenv import load_dotenv
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class PaymentSimulator:

    def __init__(self, time_limit=30):
        # ENV
        self.dotenv_path = os.path.join(os.path.dirname(__file__), '../.env.development')
        load_dotenv(self.dotenv_path)
        # RabbitMQ
        self.mq = RabbitMQ()
        # Payment queue
        self.payment_queue = os.getenv('PAYMENT_QUEUE')
        # Exchange bus
        self.exchange = os.getenv('EXCHANGE_BUS')
        # Bing key
        self.bind_key = os.getenv('PAYMENT_BINDING')
        # Payment succeeded routing key
        self.payment_succeeded_key = os.getenv('PAYMENT_SUCCEEDED_ROUTING_KEY')
        # Payment failed routing key
        self.payment_failed_key = os.getenv('PAYMENT_FAILED_ROUTING_KEY')
        # RabbitMQ
        self.mq = RabbitMQ()
        # Time limit to close self
        self.time_limit = time_limit
        # Timeout flag
        self.timeout_flag = False

    def payment_succeeded(self, order_id, x_requestid, date):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_succeeded
        Description: Function of Payment simulator.
                     1.Sends message to RabbitMQ queue Ordering that order payment succeeded.
                     P.S:
                     It is response message for request of Ordering service to order payment.
        :param date: order date,must be the same as in order,cause live processing
        :param order_id: autoincremented order id in db
        :param x_requestid: unique id of order generated from outside
        :return: True
        """

        body_to_send = {
            "OrderId": order_id,
            "Id": x_requestid,
            "CreationDate": date
        }
        self.mq.publish(self.exchange, self.payment_succeeded_key, json.dumps(body_to_send))

    def payment_succeeded_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_succeeded_callback
        Description: Function makes and sends payment  succeeded callback to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        # SENDING SUCCEEDED MESSAGE TO ORDERING QUEUE
        self.payment_succeeded(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])

    def payment_failed(self, order_id, x_requestid, date):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_failed
        Description: Function of Payment simulator.
                     Sends message to RabbitMQ queue Ordering that order payment failed.
        :param date: order date,must be the same as in order,cause live processing
        :param order_id: autoincremented order id in db
        :param x_requestid: unique id of order generated from outside
        :return: True
        """
        load_dotenv('/.env.test')
        body = {
            "OrderId": order_id,
            "OrderStatus": "stockconfirmed",
            "BuyerName": "alice",
            "Id": x_requestid,
            "CreationDate": date
        }
        self.mq.publish(self.exchange, self.payment_failed_key, json.dumps(body))

    def payment_failed_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_failed_callback
        Description: Function makes and sends payment failed callback to Ordering queue
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        # RABBITMQ INFO
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        # BODY FROM INFO IS STRING NEED TO CONVERT TO DICT TO GET PARAMS
        dict_body = eval(body)
        # SENDING FAILED MESSAGE TO ORDERING QUEUE
        self.payment_failed(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])

    def consume_to_succeed_payment(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume_to_succeed_payment
        Description: 1. Function invokes RabbitMQ consuming and get message from Payment queue.
                     2. Invokes callback payment succeeded to send message to Ordering queue.
        """
        # TEMPORARY INVOKING OF RABBITMQ

        with self.mq:
            # BIND
            self.mq.bind(self.payment_queue, self.exchange, self.bind_key)
            self.mq.channel.basic_consume(queue=self.payment_queue, on_message_callback=self.payment_succeeded_callback,
                                          auto_ack=True)
            # Start consuming messages until getting message or time limit end
            start_time = time.time()
            while True:
                self.mq.channel.connection.process_data_events()
                if time.time() - start_time >= self.time_limit:  # Time limit
                    self.mq.channel.stop_consuming()
                    self.timeout_flag = True
                    break
        return self.timeout_flag

    def consume_to_fail_payment(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume_to_fail_payment
        Description: 1. Function invokes RabbitMQ consuming and get message from Payment queue.
                     2. Invokes payment_failed_callback to send message to Ordering queue.
        """
        # TEMPORARY INVOKING OF RABBITMQ
        with self.mq:
            # BIND
            self.mq.bind(self.payment_queue, self.exchange, self.bind_key)
            self.mq.channel.basic_consume(queue='Payment', on_message_callback=self.payment_failed_callback,
                                          auto_ack=True)
            # Start consuming messages until getting message or time limit end
            start_time = time.time()
            while True:
                self.mq.channel.connection.process_data_events()
                if time.time() - start_time >= self.time_limit:  # Time limit
                    self.mq.channel.stop_consuming()
                    self.timeout_flag = True
                    break
        return self.timeout_flag


if __name__ == '__main__':
    ps = PaymentSimulator()
    # ps.consume_to_succeed_payment()  # must be order status 4 (paid) in DB
    t = threading.Thread(target=ps.consume_to_succeed_payment)
    t.start()
    t.join(40)
