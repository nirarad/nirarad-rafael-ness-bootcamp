
import os
from time import sleep
import pytest
from dotenv import load_dotenv
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import create_order, confirm_stock, payment_succeeded
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from tests.env import env_path



@pytest.fixture()
def mss_scenario():
    load_dotenv(env_path)


def test_mss_create_order_success_flow(mss_scenario):
    """
    # Test Case 1.1
    function that create new order
    """

    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    #save the orderID of new entity order from DB
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']
    #opening listening to queues
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to Basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        # check if ordering send to signalrhub simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to signalrhub simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_AWAITING_VALIDATION_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']

    # send message to rabbitMQ->catalog(check stock), rabbitMQ->ordering
    confirm_stock(order_id)
    #opening listening to queues
    with RabbitMQ() as mq:
        # excepted result : ordering->payment(items exist in stock)
        mq.consume('Payment')
        # check if ordering send to payment simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to signalrhub simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_STOCK_CONFIRMED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 2 the status of order in db is really 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']

    # send message to rabbitMQ->payment(pay), rabbitMQ->ordering
    payment_succeeded(order_id)
    #opening listening to queues
    with RabbitMQ() as mq:
        mq.consume('Catalog')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

        mq.consume('Ordering.signalrhub')
        # check if ordering send to signalrhub simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_PAID_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 3 the status of order in db is really 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']

    print("Pass - mss")






