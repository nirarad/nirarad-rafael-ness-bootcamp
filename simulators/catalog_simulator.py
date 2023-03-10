import os

from dotenv import load_dotenv

from simulators.simulator import Simulator


class CatalogSimulator(Simulator):
    """
    A class that simulate the Catalog microservice's messages traffic with RabbitMQ.
    """
    load_dotenv()

    def __init__(self):
        """
        Catalog simulator class initializer, send the parent class (The Simulator class),
        the basket class related queue,
        """
        super().__init__('Catalog')

    def validate_items_in_stock(self, body):
        """
        Method to validate that each order items quantity does not exceeding from the stock's limits.

          Parameters:
              body: The payload of the message.
        """
        # The catalog simulator sends to the ordering queue the stock validation confirmation message.
        self.send_message(body, os.environ["CATALOG_TO_ORDER_ROUTING_KEY_VALID"])

    def inform_items_not_in_stock(self, body):
        """
        Method to inform that one or more of the order items quantity does exceed from the stock's limits.

            Parameters:
                body: The payload of the message.
       """
        # The catalog simulator sends to the ordering queue the stock validation failure message.
        self.send_message(body, os.environ["CATALOG_TO_ORDER_ROUTING_KEY_INVALID"])
