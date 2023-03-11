import os
from time import sleep

from dotenv import load_dotenv

from simulators.simulator import Simulator
from utils.db.db_utils import MSSQLConnector

load_dotenv()


class BasketSimulator(Simulator):
    """
    A class that simulate the Basket microservice's messages traffic with RabbitMQ.
    """

    def __init__(self):
        """
        Basket simulator class initializer, send the parent class (The Simulator class),
        the basket class related queue,
        """
        super().__init__("Basket")

    def create_order(self, body):
        """
        Method to start the ordering process, by sending a confirmation message from the basket simulator to the ordering queue.
        Parameters:
            body: The payload of the message.
        """
        # The basket simulator sends to the ordering queue the validation for starting to create a new order.
        self.send_message(body=body, routing_key=os.environ["BASKET_TO_ORDER_ROUTING_KEY"])
        Simulator.CURRENT_ORDER_ID = self.get_order_id()
        print(
            f"Message Route: Basket -> Ordering. Routing Key: OrderStockConfirmedIntegrationEvent. Current Order ID is: {Simulator.CURRENT_ORDER_ID}")

    def verify_status_id_is_submitted(self):
        print("Verifying Status ID is submitted")
        return self.verify_state_status_id()

    def get_order_id(self):
        try:
            with MSSQLConnector() as conn:
                order_id = conn.select_query(
                    # In the below query, we fetch the last user order (max order id).
                    "SELECT MAX(o.Id) FROM ordering.orders o")
                return order_id[0]['']
        except ConnectionError as c:
            raise f'There were problem to retrieve the order id.\nException is: {c}'
