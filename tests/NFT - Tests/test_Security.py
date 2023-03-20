import os
import sys
from time import sleep

import pytest
from dotenv import load_dotenv

from tests.env import env_path
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import create_order, payment_succeeded, confirm_stock
from utils.rabbitmq.rabbitmq_send import RabbitMQ




@pytest.fixture
def security_scenario():
        load_dotenv(env_path)
        api = OrderingAPI(True)
        return api
def test_canceling_another_user_order(security_scenario):
    """
    # Test Case 5.4
    function that check if it is possible to cancel another user order
    :return: None
    """

    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('BOB'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('BOB_ID')

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

    #send api request to cancel order
    res = security_scenario.cancel_order(order_id)
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id
    # check the response code
    assert res.status_code == int(os.getenv('FORBIDDEN'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']
    print("Pass - test_canceling_another_user_order")




def test_update_another_user_order(security_scenario):
    """
    # Test Case 5.5
    function that check if it is possible to update another user's order
    :return: None
    """


    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('BOB'))
    sleep(5)
    #save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('BOB_ID')

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
    #send api request to update statun from paid to shipped
    res = security_scenario.change_status_to_shipped(order_id)
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SHIPPED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id
    # check the response code
    assert res.status_code == int(os.getenv('FORBIDDEN'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print("Pass - test_update_another_user_order")


def test_get_another_user_order(security_scenario):
    """
     # Test Case 5.6
     function that check if it is possible to get order details of another user's order
     :return: None
     """

    # saving the order id of an order of bob->BuyerId=11
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_BOB_ORDER_ID'))
        order_id = order_id[0]['Id']
    #send api request to get order details
    res = security_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('FORBIDDEN'))
    print("Pass - test_get_another_user_order")





