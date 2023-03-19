from log.logger import Log
from utils.rabbitmq.rabbitmq_receive import *
from simulators.basket import Basket
from simulators.catalog import Catalog
from simulators.payment import Payment
import pytest

l = Log()


def create_order_test_and_expected_after_step_1(number_json, db):
    """
    writer: chana kadosh
    The function executes and returns what should be after one step
    :param number_json:
    :param db:
    :return:
    """
    try:
        simulatorBasket = Basket()
        # Creating an order with a json object - (number_json)
        simulatorBasket.create_order(number_json)
        # A function that listens to messages in rabbitMQ (Listening to the 'Basket' queue)
        simulatorBasket.Messages_that_rabbitMQ_receives()
        # Compares whether the received routing key is equal to it
        assert check_routing_key('OrderStartedIntegrationEvent') == True
        # Waiting until the status becomes 1
        re = simulatorBasket.waiting_for_an_update(1, db)
        assert re == 1
        # Waiting until the status becomes 2
        re = simulatorBasket.waiting_for_an_update(2, db)
        assert re == 2
    except Exception as e:
        l.writeLog(f"Failed in-create_order_test_and_expected_after_step_1 function {e}")
        raise Exception(f"Failed in-create_order_test_and_expected_after_step_1 function {e}")


def catalog_success_test_and_expected_after_step_2(id_order, db):
    """
    writer: chana kadosh
    The function executes and returns what should be after step two
    :param id_order:
    :param db:
    :return:
    """
    try:
        simulatorCatalog = Catalog()
        # A function that listens to messages in rabbitMQ (Listening to the 'Catalog' queue)
        simulatorCatalog.Messages_that_rabbitMQ_receives()
        # Compares whether the received routing key is equal to it
        assert check_routing_key('OrderStatusChangedToAwaitingValidationIntegrationEvent') == True
        simulatorCatalog.catalog_in_stock(id_order)
        # Waiting until the status becomes 3.
        re = simulatorCatalog.waiting_for_an_update(3, db)
        assert re == 3
    except Exception as e:
        l.writeLog(f"Failed in-catalog_success_test_and_expected_after_step_2 function {e}")
        raise Exception(f"Failed in-catalog_success_test_and_expected_after_step_2 function {e}")


def payment_success_test_and_expected_after_step_3(id_order, db):
    """
    writer: chana kadosh
    The function executes and returns what should be after step three
    :param id_order:
    :param db:
    :return:
    """
    try:
        simulatorPayment = Payment()
        simulatorPayment.payment_success(id_order)
        # Waiting until the status becomes 4
        re = simulatorPayment.waiting_for_an_update(4, db)
        assert re == 4
    except Exception as e:
        l.writeLog(
            f"Failed in-payment_success_test_and_expected_after_step_3 function, parameter: id_order:{id_order}, {e} ")
        raise Exception(f"Failed in-payment_success_test_and_expected_after_step_3 function {e}")


def get_last_added_to_db(db):
    result = db.select_query(
        'SELECT Id FROM ordering.orders WHERE id = (SELECT MAX(id) FROM ordering.orders)')
    return result[0]['Id']


def get_count_order(db):
    result = db.select_query('SELECT count(*) FROM ordering.orders')
    return result[0]['']


def pre_conditions(start_docker):
    start_docker.start('rabbitmq:3-management-alpine')
    start_docker.start('eshop/identity.api:linux-latest')
    start_docker.start('eshop/ordering.api:linux-latest')
    start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
    start_docker.start('mcr.microsoft.com/mssql/server:2019-latest')
    start_docker.start('eshop/ordering.signalrhub:linux-latest')


def end_pre_conditions(start_docker):
    start_docker.pause('rabbitmq:3-management-alpine')
    start_docker.pause('eshop/identity.api:linux-latest')
    start_docker.pause('eshop/ordering.api:linux-latest')
    start_docker.pause('eshop/ordering.backgroundtasks:linux-latest')
    start_docker.pause('mcr.microsoft.com/mssql/server:2019-latest')
    start_docker.pause('eshop/ordering.signalrhub:linux-latest')