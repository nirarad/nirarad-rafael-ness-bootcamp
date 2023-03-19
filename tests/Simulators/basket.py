import os

from Tests.Simulators.simulator import Simulator


class BasketMock(Simulator):

    def send_new_order(self) -> None:
        self.send_message(os.getenv('BASKET_SEND_ROUTING_KEY'))

    def received_remove_basket(self) -> bool:
        return self.receive_message(os.getenv('BASKET_QUEUE')) == os.getenv('BASKET_RECEIVE_ROUTING_KEY')
