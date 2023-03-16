from utils.rabbitmq.eshop_rabbitmq_events import confirm_stock, reject_stock
from utils.rabbitmq.rabbitmq_receive import RabbitMQ


class CatalogSimulator:

    def __init__(self):
        # RabbitMQ
        self.mq = RabbitMQ()

    def in_stock_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: in_stock_callback
        Description: Function make and send confirmed stock callback to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        dict_body = eval(body)
        # SENDING SUCCEEDED MESSAGE TO ORDERING QUEUE
        confirm_stock(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        self.mq.channel.stop_consuming()

    def not_in_stock_callback(self, ch, method, properties, body):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: not_in_stock_callback
        Description: Function make and send rejected stock callback to Ordering queue.
        :param ch: RabbitMQ channel info
        :param method: RabbitMQ method info
        :param properties: RabbitMQ properties info
        :param body: message body
        """
        # RABBITMQ INFO
        print(f"[{ch}] Method: {method}, Properties: {properties}, Body: {body}")
        # BODY FROM INFO IS STRING NEED TO CONVERT TO DICT TO GET PARAMS
        dict_body = eval(body)
        # SENDING FAILED MESSAGE TO ORDERING QUEUE
        reject_stock(dict_body['OrderId'], dict_body['Id'], dict_body['CreationDate'])
        self.mq.channel.stop_consuming()

    def confirm_stock(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: confirm_stock
        Description: Function invokes RabbitMQ consume to get message
                     from Catalog queue and sends confirmed stock callback.

        """
        try:
            # TEMPORARY INVOKING OF RABBITMQ
            with self.mq:
                # BIND
                self.mq.bind('Catalog', 'eshop_event_bus', 'OrderStatusChangedToAwaitingValidationIntegrationEvent')
                self.mq.consume('Catalog', self.in_stock_callback)
        except Exception as e:
            raise e

    def reject_stock(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: start_listen
        Description: Function invokes RabbitMQ consume to get message
                     from Catalog queue and sends rejected stock callback.
        """
        try:
            # TEMPORARY INVOKING OF RABBITMQ
            with self.mq:
                # BIND
                self.mq.bind('Catalog', 'eshop_event_bus', 'OrderStatusChangedToAwaitingValidationIntegrationEvent')
                self.mq.consume('Catalog', self.not_in_stock_callback)
        except Exception as e:
            raise e


if __name__ == '__main__':
    cat = CatalogSimulator()
    cat.confirm_stock()
