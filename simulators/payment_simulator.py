import time

from utils.rabbitmq.eshop_rabbitmq_events import payment_succeeded, payment_failed
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class PaymentSimulator:

    def __init__(self):
        self.mq = RabbitMQ()

    def payment_succeeded_callback(self, ch, method, properties, body):
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        payment_succeeded(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])

    def consume(self):
        start_time = time.time()
        with self.mq:
            self.mq.consume('Payment', self.payment_succeeded_callback)
            # mq.channel.
            # print(callback_body)
            # while True:
            #     if time.time() - start_time < 10:
            #         pass
            #     # if 10 sec pass no sense to wait
            #     elif time.time() - start_time > 10:  # Timeout after 10 seconds
            #         return False
            #     # Updating time
            #     time.sleep(0.1)


if __name__ == '__main__':
    mq = PaymentSimulator()
    mq.consume()
    # mq.payment_succeeded_callback(0, 0, 0, 0)
