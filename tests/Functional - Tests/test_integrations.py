
from time import sleep

import pytest
from dotenv import load_dotenv
import os


from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from tests.env import env_path
from utils.rabbitmq.eshop_rabbitmq_events import create_order, confirm_stock, reject_stock,payment_failed
from utils.rabbitmq.rabbitmq_send import RabbitMQ


@pytest.fixture
def Integration_scenario():
        load_dotenv(env_path)





def test_stock_reject(Integration_scenario):
    """
    # Test Case 1.2
    function that check the creation of a new order when the stock of items is not enough.
    :return: None
    """


    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    #save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    #excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # excepted result : ordering->catalog(order start check if it is possible to create order)
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

    # send message to rabbitMQ->catalog(reject stock), rabbitMQ->ordering
    reject_stock(order_id)
    sleep(20)
    # check if after step 2 the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_stock_reject')




def test_payment_failed(Integration_scenario):
    """
    # Test Case 1.3
    function that check the creation of a new order with problem in payment.
    :return: None
    """


    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    #save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    #excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # excepted result : ordering->catalog(order start check if it is possible to create order)
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


    payment_failed(order_id)
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    sleep(20)
    # check if after step 3 the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_payment_failed')

