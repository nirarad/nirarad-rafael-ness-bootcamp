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
        super().__init__(queue=PAYMENT_QUEUE_NAME, confirm_routing_key=os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_VALID"],
                         reject_routing_key=os.environ["PAYMENT_TO_ORDER_ROUTING_KEY_INVALID"])
