from utils.rabbitmq.rabbitmq_send import RabbitMQ


class BasketSimulator(RabbitMQ):
    """
    A class that simulate a Basket microservice,
    the class single responsibility is to mock the service communication with rabbitMQ (consume messages, and publish messages)
    """

    def __init__(self, body,
                 accept_user_checkout="UserCheckoutAcceptedIntegrationEvent",
                 exchange="eshop_event_bus"):
        """
        The class initializer, the single required argument is the body argument,
        which is the only one who likely to be changed each time new instance of the class will be created.
        :param body: The payload of the message we want to publish or consume
        :param accept_user_checkout: A routing key for the accept_user_checkout method
        :param exchange: The exchange name that will lead the message to their designated queue
        """
        super().__init__()
        self.__accept_user_checkout = accept_user_checkout
        self.__exchange = exchange
        self.__body = body
        self.__queue = "Basket"

    def start_consume_for_order_integration_message(self):
        """
        Method to tell the simulator to start consuming and listen if there are any message that are entering its queue.
        :return: None
        """
        self.consume(self.__queue)

    def accept_user_checkout(self):
        """
        Method that sends to the ordering service the confirmation message that the checkout process has been valid.
        :return: None
        """
        self.publish(self.__exchange, self.__accept_user_checkout, body=self.__body)
