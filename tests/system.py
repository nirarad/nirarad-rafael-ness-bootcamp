import time
from utils.docker import docker_utils
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class System:
    def __init__(self):
        self.rmq = RabbitMQ()

    def init_dockers(self):
        """
        method starts all docker containers and stops basket, catalog and payment.
        """
        print("init_dockers")
        dm = docker_utils.DockerManager()
        dm.restart('eshop/ordering.api:linux-latest')
        dm.start('eshop/ordering.signalrhub:linux-latest')
        dm.start('eshop/ordering.backgroundtasks:linux-latest')
        dm.start('eshop/identity.api:linux-latest')
        dm.start('eshop/webhooks.api:linux-latest')
        dm.start('eshop/webhooks.client:linux-latest')
        dm.start('rabbitmq:3-management-alpine')
        dm.start('eshop/catalog.api:linux-latest')
        dm.start('eshop/basket.api:linux-latest')
        dm.start('eshop/payment.api:linux-latest')
        dm.start('mongo:latest')
        dm.stop('eshop/catalog.api:linux-latest')
        dm.stop('eshop/basket.api:linux-latest')
        dm.stop('eshop/payment.api:linux-latest')
        time.sleep(15)
        # print(dm.containers_dict)

    def purge_all_queues(self):
        """
        method deletes all messages from the queues
        """
        queues = ["BackgroundTasks", "Basket", "Catalog", "Ordering", "Ordering.signalrhub", "Payment", "Webhooks"]
        for q in queues:
            self.rmq.channel.queue_purge(q)

    def start_basket_catalog_payment(self):
        """
        method starts basket, catalog and payment docker containers
        """
        dm = docker_utils.DockerManager()
        dm.start('eshop/catalog.api:linux-latest')
        dm.start('eshop/basket.api:linux-latest')
        dm.start('eshop/payment.api:linux-latest')
        time.sleep(15)
