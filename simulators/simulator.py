import os
from abc import ABC

from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class Simulator(ABC):
    """
    Class which contains general actions that a microservice simulator needs for communicating with RabbitMQ,
    """

    def __init__(self, queue):
        """
        Abstract simulator class initializer.
            Parameters:
                queue: The simulator related queue..
        """
        super().__init__()
        self.__queue = queue

    def get_first_message(self):
        """
         Method which reads the first messages from the given queue.

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
        Method to purge the given queue.
        """
        try:
            with RabbitMQ() as mq:
                mq.purge_queue(self.__queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def send_message(self, body, routing_key, exchange=os.environ["EXCHANGE"]):
        with RabbitMQ() as mq:
            try:
                mq.publish(exchange=exchange,
                           routing_key=routing_key,
                           body=body)
            except BaseException as b:
                print(b)

    def verify_stats_status_id(self, status_id):
        with MSSQLConnector() as conn:
            assert len(conn.select_query(
                # In the below query, we fetch the last user order (max order id), and check if it's OrderStatusID is equals to 1.
                "SELECT MAX(o.Id), o.OrderStatusId "
                "FROM ordering.orders o "
                "JOIN ordering.buyers b "
                "ON b.Id = o.BuyerId "
                f"WHERE o.OrderStatusId = {status_id} "
                "GROUP BY o.OrderStatusId"
            )) > 0
