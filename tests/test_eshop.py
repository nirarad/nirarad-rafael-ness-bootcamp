import pytest
from dotenv import load_dotenv
import os
import json
from utils.api.ordering_api import OrderingAPI
from utils.api.ordering_api import BearerTokenizer
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_receive import callback
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from simulator.basket import *
from simulator.catalog import *
from simulator.catalog import *


@pytest.fixture()
def eShop():
    load_dotenv('test.env')
    return OrderingAPI()


@pytest.mark.test
def test_create_order(eShop):
    try:
        create_order(1)
        with MSSQLConnector as sql:
            result = sql.select_query(
                'SELECT ordering.orders.Id from ordering.orders where ordering.orders.OrderStatusId = 1')
            print(result)
    except Exception:
        print("ERROR")


def test_update(eShop):
    pass


def test_cancel(eShop):
    pass


def test_payment_succeeded(eShop):
    pass


def test_payment_failed(eShop):
    pass


def test_confirm_stock(eShop):
    pass


def test_reject_stock(eShop):
    pass


def test_order_tracking(eShop):
    pass


def test(eShop):
    pass
