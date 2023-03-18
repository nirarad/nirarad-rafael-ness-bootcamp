import threading

from tests.scenarios.scenarios import *


class CreateOrderThread(threading.Thread):
    """
    Threading class to simulate order creation process.
    """

    def __init__(self, goal, flag):
        """
        Initializer for the CreateOrderThread class.
        Parameters:
            goal: The amount of times that the thread will perform its operation.
            flag: A flag for telling the thread to stop running.
        """
        super().__init__()
        self.goal = goal
        self.flag = flag

    def run(self):
        for i in range(1, self.goal + 1):
            # If the flag is set, stop the thread process.
            if self.flag.is_set():
                break
            else:
                # Validate order creation - after that action the order status is 2
                assert order_submission_scenario()
                # Validate stock confirmation - after that action the order status is 3
                assert catalog_stock_confirmation_scenario()
                # Validate payment - after that action the order status is 4
                assert payment_confirmation_scenario()
                # Validate shipping - after that action the order status is 5
                assert ship_api_request_scenario()


class GetOrdersRequestsThread(threading.Thread):
    """
    Threading class to simulate ddos attack by perform an endless api requests.
    """

    def __init__(self, flag):
        """
        Initializer for the CreateOrderThread class.
        Parameters:
            flag: A flag for telling the thread to stop running.
        """
        super().__init__()
        self.flag = flag

    def run(self):
        # Send endless api requests to get the orders, until the flag is set.
        while True:
            get_orders_api_request_scenario()
            if self.flag.is_set():
                break
