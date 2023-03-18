from dotenv import load_dotenv

from config.constants import *
from simulators.service_simulator import ServiceSimulator

load_dotenv()


class PaymentSimulator(ServiceSimulator):

    def __init__(self):
        """
        Payment simulator class initializer.
        """
        super().__init__(queue=PAYMENT_QUEUE_NAME, confirm_routing_key=PAYMENT_TO_ORDER_ROUTING_KEY_VALID,
                         reject_routing_key=PAYMENT_TO_ORDER_ROUTING_KEY_INVALID)
