import pprint
import uuid

from utils.rabbitmq.eshop_rabbitmq_events import create_order
from utils.rabbitmq.rabbitmq_receive import RabbitMQ
from utils.testcase.jsondatareader import JSONDataReader


class BasketSimulator:

    def __init__(self):
        # RabbitMQ
        self.mq = RabbitMQ()
        self.data = JSONDataReader('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/ORDERS_DATA.json')
        self.sent_order = None
        self.response_message = None

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
        self.response_message = eval(body)
        self.mq.channel.stop_consuming()

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
            self.mq.bind('Basket', 'eshop_event_bus', 'OrderStartedIntegrationEven')
            self.mq.consume('Basket', self.callback)

    def place_order(self, order_to_send):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: place_order
        Description: Function sending message to RabbitMQ to Ordering queue create order.
        """
        self.sent_order = create_order(order_to_send)


if __name__ == '__main__':
    bs = BasketSimulator()
    order = bs.data.get_json_order('alice_normal_order', str(uuid.uuid4()))
    bs.place_order(order)
    print('\n')
    pprint.pprint(bs.sent_order)
    print('\n')
    bs.consume()
    print('\n')
    pprint.pprint(bs.response_message)
