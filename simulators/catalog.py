from simulators.base import Base


class Catalog(Base):
    def __init__(self):
        super().__init__("Catalog")

    def catalog_in_stock(self, id):
        """
        writer: chana kadosh
        Confirmation that it is in the catalog: send the routing key to the father.
        :param id: Order Number
        :return:
        """
        self.Receives_a_routing_key_to_rabbitMQ("OrderStockConfirmedIntegrationEvent", id)

    def catalog_out_of_stock(self, id):
        """
        writer: chana kadosh
        Confirmation that it is in the catalog: send the routing key to the father.
       :param id: Order Number
       :return:
        """
        self.Receives_a_routing_key_to_rabbitMQ("OrderStockRejectedIntegrationEvent", id)




