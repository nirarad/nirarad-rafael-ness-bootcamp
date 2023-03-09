from utils.rabbitmq.rabbitmq_send import RabbitMQ


class PaymentSimulator(RabbitMQ):

    def receive_order_status_changed_to_stock_confirmed(self):
        pass

    def send_order_payment_failed_message(self):
        pass

    def send_order_payment_succeeded_message(self):
        pass
