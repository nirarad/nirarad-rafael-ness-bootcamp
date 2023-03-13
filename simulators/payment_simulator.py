from utils.rabbitmq.eshop_rabbitmq_events import payment_succeeded, payment_failed
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class PaymentSimulator:

    def __init__(self):
        self.mq = RabbitMQ()

    @staticmethod
    def payment_succeeded_callback(ch, method, properties, body):
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        payment_succeeded(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        ch.stop_consuming()

    @staticmethod
    def payment_failed_callback(ch, method, properties, body):
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        payment_failed(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        ch.stop_consuming()

    def start_listen(self, event):
        if event == 'succeeded':
            with self.mq:
                self.mq.consume('Payment', self.payment_succeeded_callback)
        if event == 'fail':
            with self.mq:
                self.mq.consume('Payment', self.payment_failed_callback)


if __name__ == '__main__':
    mq = PaymentSimulator()
    mq.start_listen('succeeded')
