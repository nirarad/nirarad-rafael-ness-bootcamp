import os
import time

import dotenv
import pytest
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector

from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_utils import clear_all_queues_msg
from utils.signalrhub import Signalrhub

from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ

from utils.simulators.basket import Basket
from utils.simulators.catalog import Catalog
from utils.simulators.payment import Payment


@pytest.fixture(scope="class")
def setup(request):
    dm = DockerManager()
    clear_all_queues_msg()
    rbtMQ = RabbitMQ()
    db = MSSQLConnector()
    config = dotenv.dotenv_values(
        dotenv_path=dotenv.find_dotenv("../.env"))
    log = Exceptions_logs(str(time.strftime("%m-%d-%Y_%H.%M", time.localtime())))

    basket = Basket(rbtMQ, log)
    catalog = Catalog(rbtMQ, log)
    payment = Payment(rbtMQ, log)
    signalrhub = Signalrhub(rbtMQ, log)
    api = OrderingAPI(username='alice', password='Pass123%24')
    request.cls.dm = dm

    request.cls.rbtMQ = rbtMQ
    request.cls.db = db
    request.cls.config = config
    request.cls.basket = basket
    request.cls.catalog = catalog
    request.cls.payment = payment
    request.cls.api = api
    request.cls.signalrhub = signalrhub
    request.cls.log = log
    yield  # tear down
    clear_all_queues_msg()
    # db.close()
