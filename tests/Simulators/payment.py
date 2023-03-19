import os

from Tests.Simulators.simulator import Simulator


class PaymentMock(Simulator):

    def send_confirmed_payment(self, order_id) -> None:
        self.send_message(
            os.getenv('PAYMENT_SEND_SUCCEEDED_ROUTING_KEY'), order_id)

    def send_rejected_payment(self, order_id) -> None:
        self.send_message(
            os.getenv('PAYMENT_SEND_FAILED_ROUTING_KEY'), order_id)

    def received_stock_confirmed(self) -> bool:
        return self.receive_message(os.getenv('PAYMENT_QUEUE')) == os.getenv('PAYMENT_RECEIVE_ROUTING_KEY')
