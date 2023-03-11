import os

from dotenv import load_dotenv

from simulators.simulator import Simulator

load_dotenv()


class PaymentSimulator(Simulator):

    def __init__(self):
        """
        Payment simulator class initializer, sends the parent class (The Simulator class),
        the payment class related queue name.
        """
        super().__init__('Payment')

    def validate_payment(self, body):
        """
        Method to validate that Payment process.
        Parameters:
          body: The payload of the message.
        """
        # The payment simulator sends to the ordering queue the payment validation message.
        self.send_message(body=body, routing_key=os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_VALID"])
        print("Message Route: Catalog -> Ordering. Routing Key: OrderStatusChangedToStockConfirmedIntegrationEvent")

    def inform_payment_process_failed(self, body):
        """
        Method to inform that the payment process has failed.
        Parameters:
            body: The payload of the message.
       """
        # The catalog simulator sends to the ordering queue the stock validation failure message.
        self.send_message(body=body, routing_key=os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_INVALID"])

    def verify_status_id_is_paid(self, timeout=150):
        return self.verify_state_status_id(timeout=timeout)

