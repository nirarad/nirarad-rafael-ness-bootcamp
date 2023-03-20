import os
import sys
from time import sleep

import pytest
from dotenv import load_dotenv


from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from tests.env import env_path
from utils.rabbitmq.eshop_rabbitmq_events import create_order
from utils.rabbitmq.rabbitmq_send import RabbitMQ




@pytest.fixture
def Unauthorized_scenario():
        load_dotenv(env_path)
        api = OrderingAPI(False)
        return api




def test_get_order_by_id_in_status_unauthorized(Unauthorized_scenario):
    """
    # Test Case 5.1
    function that check if it possibly to get data about order without logging into the system
    :return: None
    """

    # saving the order id of an order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_RAND_ORDER_ID'))
        order_id = order_id[0]['Id']

    #send api request to get order details
    res = Unauthorized_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('UNAUTHORIZED'))
    print("Pass - test_get_order_by_id_in_status_unauthorized")



def test_cancel_order_in_status_unauthorized(Unauthorized_scenario):
    """
     # Test Case 5.2
     function that : check if it possibly to cancel order without logging into the system
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

    #send api request to cancel order
    res = Unauthorized_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('UNAUTHORIZED'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']
    print("Pass - test_cancel_order_in_status_unauthorized")


def test_update_order_in_status_unauthorized(Unauthorized_scenario):
    """
     # Test Case 5.3
     function that check if it possibly to update order without logging into the system
     :return: None
     """

    # saving the order id of an order in status 4
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_IN_STATUS_4'))
        order_id = order_id[0]['Id']
    #send api request to update statun from paid to shipped
    res = Unauthorized_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('UNAUTHORIZED'))

    # check if after api response the status of order in db is 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print("Pass - test_update_order_in_status_unauthorized")




