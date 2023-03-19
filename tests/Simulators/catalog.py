import os

from Tests.Simulators.simulator import Simulator


class CatalogMock(Simulator):

    def send_valid_stock(self, order_id) -> None:
        self.send_message(
            os.getenv('CATALOG_SEND_CONFIRMED_ROUTING_KEY'), order_id)

    def send_invalid_stock(self, order_id) -> None:
        self.send_message(
            os.getenv('CATALOG_SEND_REJECTED_ROUTING_KEY'), order_id)

    def received_check_stock(self) -> bool:
        return self.receive_message(os.getenv('CATALOG_QUEUE')) == os.getenv('CATALOG_RECEIVE_ROUTING_KEY')
