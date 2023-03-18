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
    Abstract Class which represent an abstract service simulator.
    Contains methods that allows the simulator and child classes to communicate with RabbitMQ and SQL Server.
    """

    # Will update according to the current id of the processed order.
    CURRENT_ORDER_ID = 0

    def __init__(self, queue):
        """
        Abstract simulator class initializer.
        Parameters:
            queue: The child service simulator class representative queue's name.
        """
        self.queue = queue

    def get_first_message(self, timeout=300):
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

    def send_message(self, body, routing_key, exchange=os.environ["EXCHANGE"]):
        """
        Method to publish a given message to RabbitMQ.
        Parameters:
            body: The message pyload.
            routing_key: The message routing key.
            exchange: The exchange of the message.
        """
        with RabbitMQ() as mq:
            mq.publish(exchange=exchange,
                       routing_key=routing_key,
                       body=json.dumps(body))

    def verify_state_status_id(self, status_id=None, timeout=300):
        """
        Method to validate that the current order status value is the expected value for the order state.
        Parameters:
            status_id: The expected order status id.
            timeout: The max number of seconds for trying to verify the current order status.
        Returns:
            True if the current processed order status its equal to the expected value, False otherwise.
        """
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
                        # In the below query, we fetch the last inserted order status id
                        # and checks if its equal to the excreted value.
                        "SELECT o.OrderStatusId "
                        "FROM ordering.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {Simulator.CURRENT_ORDER_ID}"))
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
            order_id = Simulator.CURRENT_ORDER_ID
        print(f"Validate id id {status_id}...")
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last inserted order status id
                        # and checks if its equal to the excreted value.
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
        """
        Method to get the maximum order id in the ordering table.
        Returns:
             The maximum order id in the ordering table.
        """
        try:
            with MSSQLConnector() as conn:
                order_id = conn.select_query(
                    # In the below query, we fetch the last inserted user order (according to the max order id).
                    "SELECT MAX(o.Id) FROM ordering.orders o")
                return order_id[0]['']
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the order id.\nException is: {c}')

    @staticmethod
    def get_amount_of_message_in_queue(queue_name):
        """
        Method to ge the amount of messages in a given RabbitMQ queue.
        Parameters:
             queue_name: The queue name to get the message amount from.
        Returns:
            The amount of messages in the given RabbitMQ queue.
        """
        try:
            with RabbitMQ() as mq:
                return mq.get_number_of_messages_in_queue(queue_name)
        except BaseException as c:
            raise BaseException(f'There were problem to count the number of messages.\nException is: {c}')

    @staticmethod
    def get_number_of_seconds_to_consume_single_waiting_message(queue_name):
        """
        Method to measure the time is taking for the service to consume a single message from a given RabbitMQ queue.
        Parameters:
            queue_name: The queue name to consume the message from.
        Returns:
            The message consumption time.
        """
        try:
            counter = 0
            with RabbitMQ() as mq:

                # Check if the given queue is empty.
                is_empty = mq.validate_queue_is_empty_once(queue_name)

                # In case the given queue is not empty, consume the message and measure the consumption time.
                while not is_empty:
                    is_empty = mq.validate_queue_is_empty_once(queue_name)
                    counter += 1
                    time.sleep(1)
            return counter
        except BaseException as c:
            raise BaseException(f'There were problem with accessing the {queue_name} queue.\nException is: {c}')

    @staticmethod
    def select_top_n_orders_with_same_status(mssql_connector, status_number_1, status_number_2, amount_of_orders, timeout):
        """
        Method to check if a given amount of top orders are in the same status.
        Parameters:
            mssql_connector: The MSSQLConnector Object to use.
            status_number_1: The first possible status number to check.
            status_number_2: The second possible status number to check.
            amount_of_orders: The amount of orders with the expected status.
            timeout: The max time for the operation to take.
        Returns:
            True if there are the given amount of top orders are in the same status and False otherwise.
        """
        try:
            for _ in range(timeout):
                # Select the sum of the top n order status id values.
                sum_of_ids = mssql_connector.select_query(
                    f"SELECT SUM(subquery.OrderStatusId) FROM (SELECT TOP {amount_of_orders} OrderStatusId FROM ordering.orders) AS subquery"
                )

                # If the query result is equal for the amount of order multiply the order status id value,
                # return true.
                if int(sum_of_ids[0]['']) == status_number_2 * amount_of_orders or int(
                        sum_of_ids[0]['']) == status_number_1 * amount_of_orders:
                    return True
                else:
                    time.sleep(1)
            return False
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the order id.\nException is: {c}')
