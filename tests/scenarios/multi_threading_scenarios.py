import threading

from tests.scenarios.scenarios import *


class CreateOrderThread(threading.Thread):
    """
    Threading class to simulate order creation.
    """

    def __init__(self, goal, event):
        super().__init__()
        self.goal = goal
        self.event = event

    def run(self):
        for i in range(1, self.goal + 1):
            if self.event.is_set():
                break
            else:
                # Create order - after that action - order status is 2
                assert order_submission_scenario()
                # Validate stock - after that action - order status is 3
                assert catalog_stock_confirmation_scenario()
                # Validate payment - after that action - order status is 4
                assert payment_confirmation_scenario()
                # Validate shipping - after that action - order status is 5
                assert ship_api_request_scenario()


class GetOrdersRequestsThread(threading.Thread):
    """
    Threading class to simulate ddos attack by perform an endless api requests.
    """

    def __init__(self, event):
        super().__init__()
        self.event = event

    def run(self):
        while True:
            get_orders_api_request_scenario()
            if self.event.is_set():
                break
