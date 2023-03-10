from abc import abstractmethod, ABC


class Simulator(ABC):
    """
    Class which contains general actions that a microservice simulator needs for communicating with RabbitMQ,
    """

    def read_first_message(self):
        """
        Abstract method to return the first queue message
        """
        pass

    @abstractmethod
    def purge_queue(self):
        """
        Abstract method to purge the queue
        """
        pass
