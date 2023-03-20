import os
import sys
from time import sleep

import pytest
from dotenv import load_dotenv

from tests.env import env_path
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.eshop_rabbitmq_events import create_order, payment_succeeded, confirm_stock
from utils.rabbitmq.rabbitmq_send import RabbitMQ




@pytest.fixture
def Realiability_scenario():
        load_dotenv(env_path)


#------------------AFTER SENT MESSAGE---------------------------
def test_recovery_after_step_one(Realiability_scenario):
    """
    # Test Case 7.1
    function that check the ability of system to recover from fall
    :return: None
    """


    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']

    ordering_service = DockerManager()
    ordering_service.stop('eshop/ordering.api:linux-latest')
    sleep(5)
    ordering_service.start('eshop/ordering.api:linux-latest')


    # send message to rabbitMQ->catalog(check stock), rabbitMQ->ordering
    confirm_stock(order_id)
    with RabbitMQ() as mq:
        # excepted result : ordering->payment(items exist in stock)
        mq.consume('Payment')
        # check if ordering send to payment simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 2 the status of order in db is really 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']

        # send message to rabbitMQ->payment(pay), rabbitMQ->ordering
    payment_succeeded(order_id)
    with RabbitMQ() as mq:
        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        # check if after step 3 the status of order in db is really 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print('Pass - test_recovery_after_step_one')


def test_recovery_in_step_2(Realiability_scenario):
    """
    # Test Case 7.2
    function that check the ability of system to recover from fall
    :return: None
    """

    # send message to rabbitMQ->create new order , rabbitMQ->ordering

    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']



    # send message to rabbitMQ->catalog(check stock), rabbitMQ->ordering
    confirm_stock(order_id)

    ordering_service = DockerManager()
    ordering_service.stop('eshop/ordering.api:linux-latest')
    sleep(5)
    ordering_service.start('eshop/ordering.api:linux-latest')
    with RabbitMQ() as mq:
        # excepted result : ordering->payment(items exist in stock)
        mq.consume('Payment')
        # check if ordering send to payment simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 2 the status of order in db is really 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']

    # send message to rabbitMQ->payment(pay), rabbitMQ->ordering
    payment_succeeded(order_id)
    with RabbitMQ() as mq:
        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 3 the status of order in db is really 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print('Pass - test_recovery_in_step_2')

#------------------BEFORE SENT MESSAGE---------------------------
def test_recovery_before_step_1(Realiability_scenario):
    """
    # Test Case 7.3
    function that check the ability of system to recover from fall
    :return: None
    """
    ordering_service = DockerManager()
    ordering_service.stop('eshop/ordering.api:linux-latest')
    sleep(5)
    ordering_service.start('eshop/ordering.api:linux-latest')
    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']

    # send message to rabbitMQ->catalog(check stock), rabbitMQ->ordering
    confirm_stock(order_id)
    with RabbitMQ() as mq:
        # excepted result : ordering->payment(items exist in stock)
        mq.consume('Payment')
        # check if ordering send to payment simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 2 the status of order in db is really 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']

    # send message to rabbitMQ->payment(pay), rabbitMQ->ordering
    payment_succeeded(order_id)
    with RabbitMQ() as mq:
        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 3 the status of order in db is really 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print('Pass - test_recovery_before_step_one')









