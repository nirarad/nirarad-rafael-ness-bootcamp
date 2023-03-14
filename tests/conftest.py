import os
import time

import dotenv
import pytest
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.signalrhub import Signalrhub
from utils.simulators.basket import Basket
from utils.simulators.catalog import Catalog
from utils.simulators.payment import Payment
import logging


@pytest.fixture(scope="class")
def setup(request):
    db = log = None
    dm = DockerManager()
    # dm.start_for_tests()
    # time.sleep(5)
    rbtMQ = RabbitMQ()
    if MSSQLConnector().conn is None:
        db = MSSQLConnector()
    config = dotenv.dotenv_values(
        dotenv_path=dotenv.find_dotenv("../.env"))
    if log is None:
        log = Exceptions_logs(str(time.strftime("%m-%d-%Y_%H.%M", time.localtime())))
    basket = Basket(rbtMQ, log)
    catalog = Catalog(rbtMQ, log)
    payment = Payment(rbtMQ, log)
    signalrhub = Signalrhub(rbtMQ, log)
    api = OrderingAPI()
    # logging.basicConfig(filename='../logs/eSohp.log', datefmt='%m/%d/%y %I:%M:%S %p', filemode='a', encoding='utf-8', level=logging.DEBUG)

    request.cls.dm = dm
    request.cls.rbtMQ = rbtMQ
    request.cls.db = db
    request.cls.config = config
    request.cls.basket = basket
    request.cls.catalog = catalog
    request.cls.payment = payment
    request.cls.api = api
    request.cls.signalrhub = signalrhub
    # request.cls.log = logging.getLogger("../logs/eSohp.log")
    request.cls.log = log
    yield  # tear down
    # logging.shutdown()
    if MSSQLConnector().conn is not None:
        db.close()
