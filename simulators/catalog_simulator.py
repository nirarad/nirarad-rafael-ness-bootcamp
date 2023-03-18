import json
import os
import time

from dotenv import load_dotenv
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class CatalogSimulator:

    def __init__(self, time_limit=30):
        # ENV
        self.dotenv_path = os.path.join(os.path.dirname(__file__), '../.env.development')
        load_dotenv(self.dotenv_path)
        # RabbitMQ
        self.mq = RabbitMQ()
        # Catalog queue
        self.catalog_queue = os.getenv('CATALOG_QUEUE')
        # Exchange bus
        self.exchange = os.getenv('EXCHANGE_BUS')
        # Bing key
        self.bind_key = os.getenv('CATALOG_BINDING')
        # Catalog stock confirmed routing key
        self.catalog_in_stock_key = os.getenv('CONFIRM_STOCK_ROUTING_KEY')
        # Catalog stock confirmed routing key
        self.catalog_not_in_stock_key = os.getenv('REJECT_STOCK_ROUTING_KEY')
        # RabbitMQ
        self.mq = RabbitMQ()
        # Time limit to close self
        self.time_limit = time_limit
        # Timeout flag
        self.timeout_flag = False

    def confirm_stock(self, order_id, x_requestid, date):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: confirm_stock
        Description: Function of Catalog simulator.
                     1.Sends message to RabbitMQ queue Ordering that items in stock
                     P.S:
                     It is response message for request of Ordering service to check items in stock.
        :param date: server generated date
        :param order_id: autoincremented order id in db
        :param x_requestid: unique id of order generated from outside
        """
        body = {
            "OrderId": order_id,
            "Id": x_requestid,
            "CreationDate": date
        }
        self.mq.publish(self.exchange, self.catalog_in_stock_key, json.dumps(body))

    def in_stock_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: in_stock_callback
        Description: Function make and send confirmed stock callback to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        # SENDING SUCCEEDED MESSAGE TO ORDERING QUEUE
        self.confirm_stock(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])

    def reject_stock(self, order_id, x_requestid, date):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: reject_stock
        Description: Function of Catalog simulator.
                     1.Sends message to RabbitMQ queue Ordering that items not in stock
                     P.S:
                     It is response message for request of Ordering service to check items in stock.
        :param date: server generated date
        :param order_id: autoincremented order id in db
        :param x_requestid: unique id of order generated from outside
        """
        body = {
            "OrderId": order_id,
            "OrderStockItems": [
                {
                    "ProductId": 1,
                    "HasStock": False
                }
            ],
            "Id": x_requestid,
            "CreationDate": date
        }
        self.mq.publish(self.exchange, self.catalog_not_in_stock_key, json.dumps(body))

    def not_in_stock_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: not_in_stock_callback
        Description: Function make and send rejected stock callback to Ordering queue.
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
        self.reject_stock(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])

    def consume_to_confirm_stock(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume_to_confirm_stock
        Description: Function invokes RabbitMQ consume to get message
                     from Catalog queue and sends confirmed stock callback.

        """
        # TEMPORARY INVOKING OF RABBITMQ
        with self.mq:
            # BIND
            self.mq.bind(self.catalog_queue, self.exchange, self.bind_key)
            # Set up a consumer with the callback function
            self.mq.channel.basic_consume(queue=self.catalog_queue, on_message_callback=self.in_stock_callback,
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

    def consume_to_reject_stock(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume_to_reject_stock
        Description: Function invokes RabbitMQ consume to get message
                     from Catalog queue and sends rejected stock callback.
        """

        # TEMPORARY INVOKING OF RABBITMQ
        with self.mq:
            # BIND
            self.mq.bind(self.catalog_queue, self.exchange, self.bind_key)
            self.mq.channel.basic_consume(queue=self.catalog_queue, on_message_callback=self.not_in_stock_callback,
                                          auto_ack=True)
            # Start consuming messages until getting message or time limit end
            start_time = time.time()
            while True:
                self.mq.channel.connection.process_data_events()
                if time.time() - start_time >= self.time_limit:  # Time limit
                    self.timeout_flag = True
                    break
        return self.timeout_flag


if __name__ == '__main__':
    cat = CatalogSimulator()
    # cat.consume_to_confirm_stock()
    cat.consume_to_reject_stock()
