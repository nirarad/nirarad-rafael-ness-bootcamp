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
        Basket simulator class initializer, send the parent class (The Simulator class),
        the basket class related queue,
        """
        super().__init__('Basket')

    def create_order(self, body):
        """
        Method to start the ordering process, by sending a confirmation message from the basket simulator to the ordering queue.

            Parameters:
                body: The payload of the message.
        """
        # The basket simulator sends to the ordering queue the validation for starting to create a new order.
        self.send_message(body, os.environ["BASKET_TO_ORDER_ROUTING_KEY"])