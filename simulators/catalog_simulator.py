import os
import threading

from dotenv import load_dotenv

from utils.rabbitmq.eshop_rabbitmq_events import payment_succeeded, payment_failed
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class PaymentSimulator:

    def __init__(self, timeout=10):
        # Separate consume thread handler
        self.consume_thread = None
        # RabbitMQ
        self.mq = RabbitMQ()
        # Time to wait
        self.timeout = timeout

    @staticmethod
    def payment_succeeded_callback(ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_succeeded_callback
        Description: 1. Function getting callback from Payment queue.
                     2. Sends payment succeeded message to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body (order to pay) from ordering api
        """
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        payment_succeeded(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        ch.stop_consuming()

    @staticmethod
    def payment_failed_callback(ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: payment_failed_callback
        Description: 1. Function getting callback from Payment queue.
                     2. Sends payment failed message to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body (order to pay) from ordering api
        """
        # RABBITMQ INFO
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        # BODY FROM INFO IS STRING NEED TO CONVERT TO DICT TO GET PARAMS
        dict_body = eval(body)
        # SENDING MESSAGE TO ORDERING QUEUE
        payment_failed(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        # MESSAGE SENT THEN SHUT CONSUMING
        ch.stop_consuming()

    def start_listen(self, event):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: start_listen
        Description: 1. Function invokes RabbitMQ consuming and get message from Payment queue.
                     2. Sends payment failed or succeeded message to Ordering queue.
        :param event: event to invoke
        """
        try:
            if load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test') is False:
                raise Exception('ENV in Basket sim in start listen path broken')
            # TEMPORARY INVOKING OF RABBITMQ
            with self.mq:
                # ROUTING KEY TO BIND IN PAYMENT QUEUE,ORDERING API SENDS MESSAGES TO HIM
                routing_key = os.getenv('PAYMENT_BINDING')
                # BIND ROUTING KEY
                self.mq.bind('Payment', 'eshop_event_bus', routing_key)
                # EVENT TO INVOKE
                if event == 'succeeded':
                    # INVOKE CONSUME VIA THREAD TO SHUT AFTER TIME
                    self.consume_thread = threading.Thread(target=self.mq.consume,
                                                           args=('Payment', self.payment_succeeded_callback))
                    self.consume_thread.start()
                    self.consume_thread.join(self.timeout)

                elif event == 'fail':
                    self.consume_thread = threading.Thread(target=self.mq.consume,
                                                           args=('Payment', self.payment_failed_callback))
                    self.consume_thread.start()
                    self.consume_thread.join(self.timeout)

                else:
                    raise Exception("Event invoke name error ,'succeeded' or 'fail' only.")
        except Exception as e:
            raise e


if __name__ == '__main__':
    mq = PaymentSimulator()
    # mq.start_listen('succeeded')
    mq.start_listen('fail')