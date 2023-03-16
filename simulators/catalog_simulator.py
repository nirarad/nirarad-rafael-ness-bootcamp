import json
import os
import time

from dotenv import load_dotenv
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class CatalogSimulator:

    def __init__(self, time_limit=30):
        # RabbitMQ
        self.mq = RabbitMQ()
        self.time_limit = time_limit
        load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')

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
        self.mq.publish('eshop_event_bus', 'OrderStockConfirmedIntegrationEvent', json.dumps(body))

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
        load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
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
        self.mq.publish('eshop_event_bus', os.getenv('REJECT_STOCK_ROUTING_KEY'), json.dumps(body))

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
        try:
            # TEMPORARY INVOKING OF RABBITMQ
            with self.mq:
                # BIND
                self.mq.bind('Catalog', 'eshop_event_bus', 'OrderStatusChangedToAwaitingValidationIntegrationEvent')
                # Set up a consumer with the callback function
                self.mq.channel.basic_consume(queue='Catalog', on_message_callback=self.in_stock_callback,
                                              auto_ack=True)
                # Start consuming messages until getting message or time limit end
                start_time = time.time()
                while True:
                    self.mq.channel.connection.process_data_events()
                    if time.time() - start_time >= self.time_limit:  # Time limit
                        self.mq.channel.stop_consuming()
                        break
        except Exception as e:
            raise e

    def consume_to_reject_stock(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume_to_reject_stock
        Description: Function invokes RabbitMQ consume to get message
                     from Catalog queue and sends rejected stock callback.
        """
        try:
            # TEMPORARY INVOKING OF RABBITMQ
            with self.mq:
                # BIND
                self.mq.bind('Catalog', 'eshop_event_bus', 'OrderStatusChangedToAwaitingValidationIntegrationEvent')
                self.mq.channel.basic_consume(queue='Catalog', on_message_callback=self.not_in_stock_callback,
                                              auto_ack=True)
                # Start consuming messages until getting message or time limit end
                start_time = time.time()
                while True:
                    self.mq.channel.connection.process_data_events()
                    if time.time() - start_time >= self.time_limit:  # Time limit
                        self.mq.channel.stop_consuming()
                        break
        except Exception as e:
            raise e


if __name__ == '__main__':
    cat = CatalogSimulator()
    # cat.consume_to_confirm_stock()
    cat.consume_to_reject_stock()
