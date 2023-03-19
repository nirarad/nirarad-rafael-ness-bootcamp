import pytest
import os

from Tests.Simulators.simulator import Simulator
from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from Utils.Docker.docker_utils import DockerManager
from Utils.Api.ordering_api import OrderingAPI
from Utils.DB.db_functions import *

container_list = os.getenv('CONTAINERS_TO_CLOSE').split(',')


@pytest.fixture(scope="class")
def docker_manager():
    return DockerManager()


@pytest.fixture(scope="class")
def ordering_api():
    return OrderingAPI()


@pytest.fixture(scope="class")
def basket():
    return BasketMock()


@pytest.fixture(scope="class")
def catalog():
    return CatalogMock()


@pytest.fixture(scope="class")
def payment():
    return PaymentMock()


@pytest.fixture(scope="class")
def signalrhub():
    return Simulator()


@pytest.fixture(autouse=True)
def docker_setUp(docker_manager: DockerManager):
    for container in container_list:
        if container in docker_manager.containers_dict.keys():
            docker_manager.stop(container)


@pytest.fixture(autouse=True)
def rabbitMQ_setUp():
    with RabbitMQ() as mq:
        mq.purge_all()
