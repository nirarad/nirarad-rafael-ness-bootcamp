import json
import os
import time
from abc import ABC

from dotenv import load_dotenv

from constants import *
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ

load_dotenv()


class ServiceSimulator(ABC):
    """
    Abstract Class which represent an abstract service simulator.
    Contains methods that allows the simulator and child classes to communicate with RabbitMQ and SQL Server.
    """

    # Will update according to the current id of the processed order.
    CURRENT_ORDER_ID = 0

    def __init__(self, queue, routing_key=""):
        """
        Abstract service simulator class initializer.
        Parameters:
            queue: The child service simulator class representative queue's name.
        """
        self.queue = queue
        self.routing_key = routing_key
        self.exchange = exchange = os.environ["EXCHANGE"]

    def get_first_message(self, timeout=100):
        """
        Method which reads the first messages from a given queue.
        Parameters:
            timeout: The max number of seconds for trying to fetch the first message in a given queue.
        Returns:
            The first message in a given queue.
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
            return None
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def purge_queue(self):
        """
        Method to purge a given queue.
        """
        try:
            with RabbitMQ() as mq:
                mq.purge_queue(self.queue)
        except ValueError as v:
            print(v)
        except BaseException as b:
            print(b)

    def send_message(self, body, routing_key="", exchange=""):
        """
        Method to publish a given message to RabbitMQ.
        Parameters:
            body: The message pyload.
            routing_key: The message routing key.
            exchange: The exchange of the message.
        """
        with RabbitMQ() as mq:
            mq.publish(exchange=self.exchange,
                       routing_key=self.routing_key,
                       body=json.dumps(body))

    def verify_state_status_id(self, status_id=None, timeout=50):
        """
        Method to validate that the current order status value is the expected value for the order state.
        Parameters:
            status_id: The expected order status id.
            timeout: The max number of seconds for trying to verify the current order status.
        Returns:
            True if the current processed order status its equal to the expected value, False otherwise.
        """
        if status_id is None:
            if self.queue == BASKET_QUEUE_NAME:
                status_id = SUBMITTED_STATUS
            elif self.queue == CATALOG_QUEUE_NAME:
                status_id = AWAITING_VALIDATION_STATUS
            elif self.queue == PAYMENT_QUEUE_NAME:
                status_id = PAID_STATUS
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last inserted order status id
                        # and checks if its equal to the excreted value.
                        "SELECT o.OrderStatusId "
                        "FROM ordering.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {ServiceSimulator.CURRENT_ORDER_ID}"))
                    if counter > 0:
                        # Order status is equal to the excepted value.
                        return True
                    else:
                        time.sleep(1)

                # Order status is different from the excepted value.
                return False
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the status id.\nException is: {c}')

    @staticmethod
    def purge_all_queues(queues_list):
        """
        Method to purge all the given queues.
        Parameters:
            queues_list: The queues to purge.
        """
        for q in queues_list:
            with RabbitMQ() as mq:
                mq.purge_queue(q)

    @staticmethod
    def explicit_status_id_validation(status_id, timeout=300, order_id=None):
        """
        Method to explicitly validates the current order status id.
        Parameters:
            status_id: The expected order status id.
            timeout: The max number of seconds for trying to verify the current order status.
            order_id: The current processed order id.
        Returns:
            True if the current processed order status its equal to the expected value, False otherwise.
        """
        if order_id is None:
            order_id = ServiceSimulator.CURRENT_ORDER_ID
        print(f"Validate status id is {status_id}...")
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last inserted order status id
                        # and checks if its equal to the excreted value.
                        "SELECT o.OrderStatusId "
                        "FROM ordering.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {ServiceSimulator.CURRENT_ORDER_ID}"))
                    if counter > 0:
                        return True
                    else:
                        time.sleep(1)
            return False
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the status id.\nException is: {c}')

    def get_amount_of_message_in_queue(self):
        """
        Method to ge the amount of messages in a given the simulator related queue.
        Returns:
            The amount of messages in the given RabbitMQ queue.
        """
        try:
            with RabbitMQ() as mq:
                return mq.get_number_of_messages_in_queue(self.queue)
        except BaseException as c:
            raise BaseException(f'There were problem to count the number of messages.\nException is: {c}')
