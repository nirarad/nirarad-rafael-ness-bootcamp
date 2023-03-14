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
                    if actual_message is None:
                        actual_message = mq.read_first_message(self.queue)
                        time.sleep(1)
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
            raise ConnectionError(f'There were problem to retrieve the status id.\nException is: {c}')

    @staticmethod
    def purge_all_queues(queues_list):
        for q in queues_list:
            with RabbitMQ() as mq:
                mq.purge_queue(q)

    @staticmethod
    def explicit_status_id_validation(status_id, timeout=300):
        print(f"Validate id id {status_id}...")
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last user order (max order id), and check if it's OrderStatusID is equals to a given value.
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
            raise ConnectionError(f'There were problem to retrieve the status id.\nException is: {c}')

    @staticmethod
    def get_max_order_id():
        try:
            with MSSQLConnector() as conn:
                order_id = conn.select_query(
                    # In the below query, we fetch the last user order (max order id).
                    "SELECT MAX(o.Id) FROM ordering.orders o")
                return order_id[0]['']
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the order id.\nException is: {c}')

    @staticmethod
    def get_amount_of_message_in_queue(queue_name):
        try:
            with RabbitMQ() as mq:
                return mq.get_number_of_messages_in_queue(queue_name)
        except BaseException as c:
            raise BaseException(f'There were problem to count the number of messages.\nException is: {c}')

    @staticmethod
    def get_number_of_seconds_to_consume_single_waiting_message(queue_name):
        try:
            counter = 0
            with RabbitMQ() as mq:
                is_empty = mq.validate_queue_is_empty(queue_name)
                while not is_empty:
                    is_empty = mq.validate_queue_is_empty(queue_name)
                    counter += 1
                    time.sleep(1)
            return counter
        except BaseException as c:
            raise BaseException(f'There were problem with accessing the {queue_name} queue.\nException is: {c}')

    @staticmethod
    def validate_queue_id_empty(queue_name):
        try:
            with RabbitMQ() as mq:
                return mq.validate_queue_is_empty(queue_name)
        except BaseException as c:
            raise BaseException(f'There were problem to count the number of messages.\nException is: {c}')

    @staticmethod
    def select_top_n_orders_same_status(mssql_connector, status_number_1, status_number_2, amount_of_orders, timeout):
        """

        :param mssql_connector: The MSSQLConnector Object to use.
        :param status_number_1: The status number to check.
        :param status_number_2:
        :param amount_of_orders: The amount of orders with that status.
        :param timeout: The max timeout for the operation.
        :return:
        """
        try:
            for _ in range(timeout):
                sum_of_ids = mssql_connector.select_query(
                    f"SELECT SUM(subquery.OrderStatusId) FROM (SELECT TOP {amount_of_orders} OrderStatusId FROM ordering.orders) AS subquery"
                )
                print(type(sum_of_ids[0]['']))
                if int(sum_of_ids[0]['']) == status_number_2 * amount_of_orders or int(
                        sum_of_ids[0]['']) == status_number_1 * amount_of_orders:
                    return True
                else:
                    time.sleep(1)
            return False
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the order id.\nException is: {c}')