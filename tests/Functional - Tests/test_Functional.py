
import pytest
from dotenv import load_dotenv
import os

from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from tests.env import env_path
from utils.rabbitmq.eshop_rabbitmq_events import create_order_0_quantity, create_order_empty_list
from utils.rabbitmq.rabbitmq_send import RabbitMQ



@pytest.fixture
def Functional_scenario():
        load_dotenv(env_path)




def test_create_order_with_0_quantity(Functional_scenario):
    """
    # Test Case 1.4
    function that check if new order created when the list of item is contains 0 quantity of item.
    :return: None
    """
    with MSSQLConnector() as conn:
        count_row_before_order = conn.select_query(os.getenv('SELECT_COUNT_OF_ENTITY'))
        count_row_before_order = count_row_before_order[0]['cnt']

    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order_0_quantity(os.getenv('ALICE'))
    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')
        #count order
    with MSSQLConnector() as conn:
        count_row_after_order = conn.select_query(os.getenv('SELECT_COUNT_OF_ENTITY'))
        count_row_after_order = count_row_after_order[0]['cnt']
    assert count_row_after_order == count_row_before_order
    print('Pass - test_create_order_with_0_quantity')


def test_create_order_with_emtpy_list_of_items(Functional_scenario):
    """
    # Test Case 1.5
    function that check if new order created when the list of item is empty.
    :return: None
    """
    with MSSQLConnector() as conn:
        count_row_before_order = conn.select_query(os.getenv('SELECT_COUNT_OF_ENTITY'))
        count_row_before_order = count_row_before_order[0]['cnt']

    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order_empty_list(os.getenv('ALICE'))
    with RabbitMQ() as mq:
        mq.consume('Basket')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

    with MSSQLConnector() as conn:
        count_row_after_order = conn.select_query(os.getenv('SELECT_COUNT_OF_ENTITY'))
        count_row_after_order = count_row_after_order[0]['cnt']
    assert count_row_after_order == count_row_before_order
    print('Pass - test_create_order_with_emtpy_list_of_items')

