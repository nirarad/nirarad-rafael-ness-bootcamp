from simulators.base import Base


class Payment(Base):
    def __init__(self):
        super().__init__("Payment")

    def payment_failed(self, id):
        """
        writer: chana kadosh
        Failed payment: send the routing key to the father
        :param id: Order Number
        :return:
        """
        self.Receives_a_routing_key_to_rabbitMQ("OrderPaymentFailedIntegrationEvent", id)

    def payment_success(self, id):
        """
        writer: chana kadosh
        Successful payment: send the routing key to the father
        :param id: Order Number
        :return:
        """
        self.Receives_a_routing_key_to_rabbitMQ("OrderPaymentSucceededIntegrationEvent", id)

