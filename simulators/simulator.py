import json
import os
import time
from abc import ABC

from dotenv import load_dotenv

from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ

load_dotenv()


class Simulator(ABC):
    """
    Class which contains general actions that a microservice simulator needs for communicating with RabbitMQ,
    """

    CURRENT_ORDER_ID = 0

    def __init__(self, queue):
        """
        Abstract simulator class initializer.
            Parameters:
                queue: The simulator related queue..
        """
        super().__init__()
        self.queue = queue

    def get_first_message(self, timeout=300):
        """
        Method which reads the first messages from the given queue.
        Returns:
            The first message in the basket queue.
        """
        try:
            with RabbitMQ() as mq:
                actual_message = None
                for i in range(timeout):
                    time.sleep(1)
                    if actual_message is None:
                        actual_message = mq.read_first_message(self.queue)
                    else:
                        return actual_message


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
                mq.purge_queue(self.queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def send_message(self, body, routing_key, exchange=os.environ["EXCHANGE"]):
        with RabbitMQ() as mq:
            mq.publish(exchange=exchange,
                       routing_key=routing_key,
                       body=json.dumps(body))

    def verify_state_status_id(self, status_id=None, timeout=300):
        if status_id is None:
            if self.queue == 'Basket':
                status_id = 1
            elif self.queue == 'Catalog':
                status_id = 2
            elif self.queue == 'Payment':
                status_id = 4
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last user order (max order id), and check if it's OrderStatusID is equals to 1.
                        "SELECT o.OrderStatusId "
                        "FROM ordering.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {Simulator.CURRENT_ORDER_ID}"))
                    if counter > 0:
                        return True
                    else:
                        time.sleep(1)
                return False
        except ConnectionError as c:
            raise f'There were problem to retrieve the status id.\nException is: {c}'

    @staticmethod
    def purge_all_queues(queues_list):
        for q in queues_list:
            with RabbitMQ() as mq:
                mq.purge_queue(q)

    @staticmethod
    def implicit_status_id_validation(status_id, timeout=300):
        print(f"Validate id id {status_id}...")
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last user order (max order id), and check if it's OrderStatusID is equals to 1.
                        "SELECT o.OrderStatusId "
                        "FROM ordering.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {Simulator.CURRENT_ORDER_ID}"))
                    if counter > 0:
                        return True
                    else:
                        time.sleep(1)
                return False
        except ConnectionError as c:
            raise f'There were problem to retrieve the status id.\nException is: {c}'
