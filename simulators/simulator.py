from abc import abstractmethod, ABC


class Simulator(ABC):
    """
    Class which contains general actions that a microservice simulator needs for communicating with RabbitMQ,
    """

    def __init__(self, queue):
        """
        The class initializer.
        """
        super().__init__()
        self.__queue = queue

    @abstractmethod
    def get_first_message(self):
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
