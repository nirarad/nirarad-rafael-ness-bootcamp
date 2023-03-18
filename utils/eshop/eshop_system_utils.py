import time

from dotenv import load_dotenv

from simulators.service_simulator import ServiceSimulator
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ

load_dotenv()


class EShopSystem:
    """
    Static class which contains the eshop system related utilities operations.
    """

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
                        "FROM eshop.orders o "
                        f"WHERE o.OrderStatusId = {status_id} "
                        f"and o.Id = {ServiceSimulator.CURRENT_ORDER_ID}"))
                    if counter > 0:
                        return True
                    else:
                        time.sleep(1)
            return False
        except ConnectionError as c:
            raise ConnectionError(f'There were problem to retrieve the status id.\nException is: {c}')
