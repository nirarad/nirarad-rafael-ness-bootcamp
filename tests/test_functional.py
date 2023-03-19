import time

import pytest

from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
# from log.logger import Log
from utils.rabbitmq.rabbitmq_send import *
# from simulators.basket import Basket
from tests.functions_test import *

l = Log()


@pytest.fixture(autouse=True)
def clean_rabbitmq_messages():
    # prepare something ahead of all tests
    with RabbitMQ() as mq:
        mq.clean_rabbit_messages()


@pytest.fixture()
def start_connect():
    return OrderingAPI()


def start_connect_bob():
    return OrderingAPI("bob", "Pass123%24")


@pytest.fixture()
def start_mq():
    return RabbitMQ()


@pytest.fixture()
def start_docker():
    return DockerManager()


@pytest.fixture()
def start_db():
    return MSSQLConnector()


@pytest.mark.one
def test_call_the_ordering_api(start_connect):
    assert start_connect.contact_with_the_serve() == 200

@pytest.mark.functional
def test_get_order_by_id(start_connect):
    """

    get order by id
    :param start_connect:
    :return:
    """

    assert start_connect.get_order_by_id(1)['ordernumber'] == 1




@pytest.mark.sanity
def test_mss(start_connect):
    """
    Test number : 1
    writer: chana kadosh
    Create new order success flow.
    """
    pre_conditions()
    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the object number from the json file, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB.
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Confirmation of successful payment, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        payment_success_test_and_expected_after_step_3(id_order, db)


@pytest.mark.functional
def test_out_of_stock_quantity(start_connect):
    """
    Test number : 2
    Create new order with an out-of-stock quantity.
    :param start_connect:
    """
    simulatorCatalog = Catalog()
    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the amount of the product, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2.1 -- Confirmation from the catalog that is not in stock
        # The function receives - the ID of the order
        simulatorCatalog.catalog_out_of_stock(id_order)
        # step 2.2 expected Result -- The status is updated to "cancelled" (6)
        re = simulatorCatalog.waiting_for_an_update(6, db)
        assert re == 6


@pytest.mark.functional
def test_payment_failed(start_connect):
    """
    Test number: 3
    Order creation with payment failed
    :param start_connect:
    :return:
    """
    simulatorPayment = Payment()
    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the amount of the product, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Payment confirmation failed
        # The function receives - the ID of the order
        simulatorPayment.payment_failed(id_order)
        # Expected result --for step 3
        re = simulatorPayment.waiting_for_an_update(6, db)
        assert re == 6
@pytest.mark.functional
def test_create_order_with_an_empty_basket():
    """
    Test number: 4
    Creating an order with an empty basket

    :return:
    """
    with MSSQLConnector() as db:
        # Saves the amount of orders there are before the function is activated
        before = get_count_order(db)
        simulatorBasket = Basket()
        # create order
        simulatorBasket.create_order(4)
        time.sleep(5)
        # Saves the amount of orders after activating the function
        after = get_count_order(db)
        assert before == after

@pytest.mark.functional
def test_create_order(start_connect):
    """
    Test number: 18
    create order
    :return:
    """
    with MSSQLConnector() as db:
        create_order_test_and_expected_after_step_1(0, db)

@pytest.mark.functional
def test_create_order_and_confirmation_from_catalog():
    """
    Test number: 19
    The catalog test
    :return:
    """
    with MSSQLConnector() as db:
        create_order_test_and_expected_after_step_1(0, db)
        id_order = get_last_added_to_db(db)
        catalog_success_test_and_expected_after_step_2(id_order, db)

@pytest.mark.functional
def test_price_invalid():
    """
    Test number: 21
    Creating an order with an incorrect amount
    :return:
    """
    with MSSQLConnector() as db:
        before = get_count_order(db)
        simulatorBasket = Basket()
        simulatorBasket.create_order(3)
        after = get_count_order(db)
        assert after == before
@pytest.mark.functional
@pytest.mark.test_create_order_fail_with_card_type_4
def test_create_order_fail_with_card_type_4():
    """
    Test number: 16
    Creating an order with the wrong card
    Requirement: 5
    :return:
    """
    with MSSQLConnector() as db:
        # Saves the amount of orders there are before the function is activated
        before = get_count_order(db)
        simulatorBasket = Basket()
        # create order
        simulatorBasket.create_order(1)
        time.sleep(5)
        # Saves the amount of orders after activating the function
        after = get_count_order(db)
        assert before == after






if __name__ == '__main__':
    pass
