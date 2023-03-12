import os
import time

import dotenv
import pytest
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.exceptions_loging import Exceptions_logs
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.simulators.basket import Basket
from utils.simulators.catalog import Catalog
from utils.simulators.payment import Payment
import logging


@pytest.fixture(scope="class")
def setup(request):
    db = log = None
    rbtMQ = RabbitMQ()
    if MSSQLConnector().conn is None:
        db = MSSQLConnector()
    config = dotenv.dotenv_values(
        dotenv_path=dotenv.find_dotenv("../.env"))
    basket = Basket(rbtMQ)
    catalog = Catalog(rbtMQ)
    payment = Payment(rbtMQ)
    api = OrderingAPI()
    # logging.basicConfig(filename='../logs/eSohp.log', datefmt='%m/%d/%y %I:%M:%S %p', filemode='a', encoding='utf-8', level=logging.DEBUG)

    if log is None:
        log = Exceptions_logs(str(time.strftime("%m-%d-%Y_%H.%M", time.localtime())))
    request.cls.rbtMQ = rbtMQ
    request.cls.db = db
    request.cls.config = config
    request.cls.basket = basket
    request.cls.catalog = catalog
    request.cls.payment = payment
    request.cls.api = api
    # request.cls.log = logging.getLogger("../logs/eSohp.log")
    request.cls.log = log
    yield  # tear down
    # logging.shutdown()
    if MSSQLConnector().conn is not None:
        db.close()
