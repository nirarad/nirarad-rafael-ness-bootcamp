import os

from dotenv import load_dotenv

from constants import *
from simulators.service_simulator import ServiceSimulator

load_dotenv()


class PaymentSimulator(ServiceSimulator):

    def __init__(self):
        """
        Payment simulator class initializer, sends the parent class (The Simulator class),
        the payment class related queue name.
        """
        super().__init__(PAYMENT_QUEUE_NAME, os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_INVALID"],
                         os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_INVALID"])

    # def send_message_to_validate_payment(self, body):
    #     """
    #     Method to send a message to informs that the payment process has been valid.
    #     Parameters:
    #         body: The payload of the message.
    #     """
    #     # The payment simulator sends to the eshop queue the payment validation message.
    #     self.send_confirmation_message(body=body)
    #     print("Message Route: Payment -> Ordering. Routing Key: OrderPaymentSucceededIntegrationEvent")

    # def inform_payment_process_failed(self, body):
    #     """
    #     Method to send a message to inform that the payment process has failed.
    #     Parameters:
    #         body: The payload of the message.
    #    """
    #     # The payment simulator sends to the eshop queue that the payment process has been failed.
    #     self.send_confirmation_message(body=body)
    #     print("Message Route: Payment -> Ordering. Routing Key: OrderPaymentFailedIntegrationEvent")

    # def verify_status_id_is_paid(self, timeout=300):
    #     """
    #     Method to verify that the current order status is paid.
    #     Parameters:
    #         timeout: The max number of seconds for trying to validate the id.
    #     Returns:
    #         True if the current order status is paid and False otherwise.
    #     """
    #     return self.validate_order_current_status_id(timeout=timeout)
