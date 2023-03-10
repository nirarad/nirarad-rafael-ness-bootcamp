import json
import os

from dotenv import load_dotenv

from simulators.simulator import Simulator
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class BasketSimulator(Simulator):
    """
    A class that simulate the Basket microservice's messages traffic with RabbitMQ.
    """
    load_dotenv()

    def __init__(self):
        """
        The class initializer.
        """
        super().__init__('Basket')

    def create_order(self, body):
        """
        Method to start the ordering process, by sending a confirmation message from the basket simulator to the ordering queue.

            Parameters:
                body: The payload of the message.

        """
        # The basket simulator sends to the ordering queue the validation for starting to create a new order.
        with RabbitMQ() as mq:
            try:
                mq.publish(exchange=os.environ["EXCHANGE"],
                           routing_key=os.environ["BASKET_TO_ORDER_ROUTING_KEY"],
                           body=json.dumps(body))
            except BaseException as b:
                print(b)
