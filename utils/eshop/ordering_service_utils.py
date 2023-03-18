import time

from dotenv import load_dotenv

from constants import *
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ

load_dotenv()


class OrderingServiceUtils:
    """
    Static class for eshop service and queue related operations.
    """

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
    def select_top_n_orders_with_same_status(mssql_connector, status_number_1, status_number_2, amount_of_orders,
                                             timeout):
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
                    f"SELECT SUM(subquery.OrderStatusId) FROM (SELECT TOP {amount_of_orders} OrderStatusId FROM eshop.orders) AS subquery"
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

    @staticmethod
    def get_amount_of_message_in_ordering_queue():
        """
        Method to ge the amount of messages in a given the simulator related queue.
        Returns:
            The amount of messages in the given RabbitMQ queue.
        """
        try:
            with RabbitMQ() as mq:
                return mq.get_number_of_messages_in_queue(ORDERING_QUEUE_NAME)
        except BaseException as c:
            raise BaseException(f'There were problem to count the number of messages.\nException is: {c}')

    @staticmethod
    def get_max_order_id():
        """
        Method to get the maximum order id in the eshop table.
        Returns:
             The maximum order id in the eshop table.
        """
        try:
            with MSSQLConnector() as conn:
                order_id = conn.select_query(
                    # In the below query, we fetch the last inserted user order (according to the max order id).
                    "SELECT MAX(o.Id) FROM eshop.orders o")
                return order_id[0]['']
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the order id.\nException is: {c}')
