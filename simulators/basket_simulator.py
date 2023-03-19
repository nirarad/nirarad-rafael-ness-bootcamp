import json
import time
import uuid
import os
from utils.rabbitmq.rabbitmq_receive import RabbitMQ
from utils.testcase.jsondatareader import JSONDataReader
from dotenv import load_dotenv


class BasketSimulator:
    def __init__(self, time_limit=30):
        # ENV
        self.dotenv_path = os.path.join(os.path.dirname(__file__), '../.env.test')
        load_dotenv(self.dotenv_path)
        # Flag to stop simulator
        self.stop = False
        # RabbitMQ
        self.mq = RabbitMQ()
        # Basket queue
        self.basket_queue = os.getenv('BASKET_QUEUE')
        # Exchange bus
        self.exchange = os.getenv('EXCHANGE_BUS')
        # Bing key
        self.bind_key = os.getenv('BASKET_BINDING')
        # Basket routing key
        self.basket_key = os.getenv('CREATE_ORDER_ROUTING_KEY')
        # Time limit to consume
        self.time_limit = time_limit
        # Sent order is corrected by Ordering api need to handle
        self.sent_order = None
        # Message from callback handler
        self.message = None

    def create_order(self, body_to_send):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: create_order
        Description: Function of Basket simulator.
                     Sends message to RabbitMQ queue Ordering to create order.
        :param body_to_send: body to send in message
        :return: sent body with date corrected by server
        """
        if body_to_send is None:
            raise Exception('Message body is None.')
        # Sending message to RabbitMQ queue Ordering
        with self.mq:
            published_body = self.mq.publish(exchange=self.exchange,
                                             routing_key=self.basket_key,
                                             body=json.dumps(body_to_send))
        return published_body

    def callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: callback
        Description: Function gets callback from Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        # RABBITMQ INFO
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        # BODY FROM INFO IS STRING NEED TO CONVERT TO DICT TO GET PARAMS
        self.message = eval(body)

    def consume(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: consume
        Description: Function invokes RabbitMQ consume to get message
                     from Basket.

        """
        # TEMPORARY INVOKING OF RABBITMQ
        with self.mq:
            # BIND
            self.mq.bind(self.basket_queue, self.exchange, self.bind_key)
            self.mq.channel.basic_consume(queue=self.basket_queue,
                                          on_message_callback=self.callback,
                                          auto_ack=True)
            # Start consuming messages until getting message or time limit end
            start_time = time.time()
            while self.stop is not True:
                self.mq.channel.connection.process_data_events()
                if time.time() - start_time >= self.time_limit:  # Time limit
                    break
            self.stop = False


if __name__ == '__main__':
    data = JSONDataReader('test/DATA/ORDERS_DATA.json')
    bs = BasketSimulator()
    order = data.get_json_order('alice_normal_order', str(uuid.uuid4()))
    bs.create_order(order)
