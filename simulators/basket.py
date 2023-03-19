from simulators.base import Base
from utils.rabbitmq.rabbitmq_receive import check_routing_key


class Basket(Base):
    def __init__(self):

        super().__init__("Basket")

    def create_order(self, id):
        """
        writer: chana kadosh
        Creating an order: sends the routing key to the father
        :param id:
        """
        self.Receives_a_routing_key_to_rabbitMQ("UserCheckoutAcceptedIntegrationEvent", id)


