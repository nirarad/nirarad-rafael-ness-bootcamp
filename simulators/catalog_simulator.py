from utils.rabbitmq.rabbitmq_send import RabbitMQ


class CatalogSimulator(RabbitMQ):

    def receive_status_changed_to_awaiting_validation(self):
        pass

    def send_order_stock_confirmed_message(self):
        pass

    def send_order_out_of_stock_message(self):
        pass
