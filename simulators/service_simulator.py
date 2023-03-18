import json
import os
import time

from dotenv import load_dotenv

from constants import *
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ

load_dotenv()


class ServiceSimulator:
    """
    Class which represent a service simulator.
    Contains methods that allows the simulator and its child classes to communicate with the service queue.
    """

    # Will update according to the current id of the processed order.
    CURRENT_ORDER_ID = 0

    def __init__(self, queue, confirm_routing_key="", reject_routing_key="", exchange=os.environ["EXCHANGE"]):
        """
        Service simulator class initializer.
        Parameters:
            queue: The child service simulator class representative queue's name.
            confirm_routing_key: The confirmation message routing key that the simulator sends.
            exchange: The exchange of the message that being sends by teh simulator.

        """
        self.queue = queue
        self.confirm_routing_key = confirm_routing_key
        self.reject_routing_key = reject_routing_key
        self.exchange = exchange

    def get_first_message_from_service_queue(self, timeout=100):
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

    def send_confirmation_message(self, body):
        """
        Method to publish a given message to RabbitMQ.
        Parameters:
            body: The message pyload.
        """
        with RabbitMQ() as mq:
            mq.publish(exchange=self.exchange,
                       routing_key=self.confirm_routing_key,
                       body=json.dumps(body))
        if self.queue == CATALOG_QUEUE_NAME:
            print("Message Route: Catalog -> Ordering. Routing Key: OrderStockConfirmedIntegrationEvent")
        elif self.queue == PAYMENT_QUEUE_NAME:
            print("Message Route: Payment -> Ordering. Routing Key: OrderPaymentSucceededIntegrationEvent")

    def send_rejection_message(self, body):
        """
        Method to publish a given message to RabbitMQ.
        Parameters:
            body: The message pyload.
        """
        with RabbitMQ() as mq:
            mq.publish(exchange=self.exchange,
                       routing_key=self.reject_routing_key,
                       body=json.dumps(body))
        if self.queue == CATALOG_QUEUE_NAME:
            print("Message Route: Catalog -> Ordering. Routing Key: OrderStockRejectedIntegrationEvent")
        elif self.queue == PAYMENT_QUEUE_NAME:
            print("Message Route: Payment -> Ordering. Routing Key: OrderPaymentFailedIntegrationEvent")

    def validate_order_current_status_id(self, status_id=None, timeout=50):
        """
        Method to validate that the current order status value is the expected value for the current order state.
        Parameters:
            status_id: The expected order status id.
            timeout: The max number of seconds for trying to verify the current order status.
        Returns:
            True if the current processed order status its equal to the expected value, False otherwise.
        """
        if status_id is None:
            if self.queue == BASKET_QUEUE_NAME:
                status_id = SUBMITTED_STATUS
                print("Verifying Status ID is submitted...")
            elif self.queue == CATALOG_QUEUE_NAME:
                status_id = AWAITING_VALIDATION_STATUS
                print("Verifying Status ID is awaiting validation...")
            elif self.queue == PAYMENT_QUEUE_NAME:
                status_id = PAID_STATUS
                print("Verifying Status ID is paid...")
        try:
            with MSSQLConnector() as conn:
                for i in range(timeout):
                    counter = len(conn.select_query(
                        # In the below query, we fetch the last inserted order status id
                        # and checks if its equal to the excreted value.
                        "SELECT o.OrderStatusId "
                        "FROM eshop.orders o "
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
