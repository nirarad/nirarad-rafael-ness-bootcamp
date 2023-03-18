from dotenv import load_dotenv

from config.constants import *
from simulators.service_simulator import ServiceSimulator

load_dotenv()


class CatalogSimulator(ServiceSimulator):
    """
    A class that simulate the Catalog microservice's messages traffic with RabbitMQ.
    """

    def __init__(self):
        """
        Catalog simulator class initializer, send the parent class (The Service Simulator class),
        the catalog class related queue.
        """
        super().__init__(queue=CATALOG_QUEUE_NAME, confirm_routing_key=CATALOG_TO_ORDER_ROUTING_KEY_VALID,
                         reject_routing_key=CATALOG_TO_ORDER_ROUTING_KEY_INVALID)

    def verify_status_id_is_stock_confirmed(self, timeout=300):
        """
        Method to verify that the current order status is stockconfirmed.
        Parameters:
            timeout: The number of seconds for trying to validate the order status.
        Returns:
            True if the current order status is stockconfirmed and False otherwise.
        """
        print("Verifying Status ID is stockconfirmed...")
        return self.validate_order_current_status_id(status_id=STOCK_CONFIRMED_STATUS, timeout=timeout)
