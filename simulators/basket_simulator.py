import json
import os
import uuid
from datetime import datetime

from simulators.simulator import Simulator
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class BasketSimulator(Simulator):
    """
    A class that simulate the Basket microservice input and output messages to RabbitMQ.
    """

    def __init__(self):
        """
        The class initializer.
        """
        super().__init__()
        self.__queue = os.environ["BASKET_QUEUE"]

    def read_first_message(self):
        """
         Method which reads a certain amount of messages from the basket queue.
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

    @staticmethod
    def create_order(body):
        """
        Method to start the ordering process, bu sending a confirmation message from the basket simulator to the ordering queue.
        """
        request_id = str(uuid.uuid4())
        current_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with RabbitMQ() as mq:
                mq.publish(exchange=os.environ["EXCHANGE"],
                           routing_key=os.environ["BASKET_TO_ORDER_ROUTING_KEY"],
                           body=json.dumps(body.format(request_id, request_id, current_date)))
        except BaseException as b:
            print(b)
