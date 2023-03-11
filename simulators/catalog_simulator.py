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

    def validate_items_in_stock(self, body):
        """
        Method to validate that each order items quantity does not exceeding from the stock's limits.
        Parameters:
          body: The payload of the message.
        """
        # The catalog simulator sends to the ordering queue the stock validation confirmation message.
        self.send_message(body=body, routing_key=os.environ["CATALOG_TO_ORDER_ROUTING_KEY_VALID"])
        print("Message Route: Catalog -> Ordering. Routing Key: UserCheckoutAcceptedIntegrationEvent")

    def inform_items_not_in_stock(self, body):
        """
        Method to inform that one or more of the order items quantity does exceed from the stock's limits.
        Parameters:
            body: The payload of the message.
       """
        # The catalog simulator sends to the ordering queue the stock validation failure message.
        self.send_message(body=body, routing_key=os.environ["CATALOG_TO_ORDER_ROUTING_KEY_INVALID"])

    def verify_status_id_is_awaiting_validation(self, timeout=30):
        print("Verifying Status ID is awaitingvalidation...")
        return self.verify_state_status_id(timeout=timeout)

    def verify_status_id_is_stock_confirmed(self, timeout=30):
        print("Verifying Status ID is stockconfirmed...")
        return self.verify_state_status_id(status_id=3, timeout=30)
