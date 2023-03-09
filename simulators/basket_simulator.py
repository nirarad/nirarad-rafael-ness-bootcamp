from utils.rabbitmq.rabbitmq_send import RabbitMQ


class BasketSimulator(RabbitMQ):

    def receive_order_start_integration_message(self):
        pass

    def send_confirmation_message(self):
        pass

    def send_order_status_changed_to_submitted(self):
        pass


