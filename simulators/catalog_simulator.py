import os

from dotenv import load_dotenv

from simulators.simulator import Simulator

load_dotenv()


class CatalogSimulator(Simulator):
    """
    A class that simulate the Catalog microservice's messages traffic with RabbitMQ.
    """

    def __init__(self):
        """
        Catalog simulator class initializer, send the parent class (The Simulator class),
        the catalog class related queue.
        """
        super().__init__('Catalog')

    def send_message_to_validate_items_in_stock(self, body):
        """
        Method to inform that the order items are in stock.
        Parameters:
          body: The payload of the message.
        """
        # The catalog simulator sends to the ordering queue the stock validation confirmation message.
        self.send_message(body=body, routing_key=os.environ["CATALOG_TO_ORDER_ROUTING_KEY_VALID"])
        print("Message Route: Catalog -> Ordering. Routing Key: UserCheckoutAcceptedIntegrationEvent")

    def send_message_to_inform_items_not_in_stock(self, body):
        """
        Method to inform that one or more of the order items are not in stock.
        Parameters:
            body: The payload of the message.
       """
        # The catalog simulator sends to the ordering queue the stock validation failure message.
        self.send_message(body=body, routing_key=os.environ["CATALOG_TO_ORDER_ROUTING_KEY_INVALID"])
        print("Message Route: Catalog -> Ordering. Routing Key: OrderStockRejectedIntegrationEvent")

    def verify_status_id_is_awaiting_validation(self, timeout=300):
        """
        Method to verify that the current order status is awaitingvalidation.
        Parameters:
            timeout: The number of seconds for trying to validate the id.
        Returns:
            True if the current order status is awaitingvalidation and False otherwise.
        """
        print("Verifying Status ID is awaitingvalidation...")
        return self.verify_state_status_id(timeout=timeout)

    def verify_status_id_is_stock_confirmed(self, timeout=30):
        """
        Method to verify that the current order status is stockconfirmed.
        Parameters:
            timeout: The number of seconds for trying to validate the order status.
        Returns:
            True if the current order status is stockconfirmed and False otherwise.
        """
        print("Verifying Status ID is stockconfirmed...")
        return self.verify_state_status_id(status_id=3, timeout=timeout)
