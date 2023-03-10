import json
import os

from dotenv import load_dotenv

from simulators.simulator import Simulator
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class BasketSimulator(Simulator):
    """
    A class that simulate the Basket microservice input and output messages to RabbitMQ.
    """
    load_dotenv()

    def __init__(self):
        """
        The class initializer.
        """
        super().__init__(os.environ["BASKET_QUEUE"])

    def get_first_message(self):
        """
         Method which reads the first messages from the basket queue.
        :return: The first message in the basket queue.
        """
        try:
            with RabbitMQ() as mq:
                return mq.read_first_message(self.__queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def purge_queue(self):
        """
        Method to purge the basket queue.
        """
        try:
            with RabbitMQ() as mq:
                mq.purge_queue(self.__queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def create_order(self, body):
        """
        Method to start the ordering process, bu sending a confirmation message from the basket simulator to the ordering queue.
        """
        # try:
        with RabbitMQ() as mq:
            try:
                mq.publish(exchange=os.environ["EXCHANGE"],
                           routing_key=os.environ["BASKET_TO_ORDER_ROUTING_KEY"],
                           body=json.dumps(body))
            except BaseException as b:
                print(b)
