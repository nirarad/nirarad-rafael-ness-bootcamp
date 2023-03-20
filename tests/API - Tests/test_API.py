
from time import sleep
import pytest
from dotenv import load_dotenv
import os

from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.eshop_rabbitmq_events import create_order, confirm_stock, payment_succeeded, reject_stock
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from tests.env import env_path


@pytest.fixture
def api_scenario():
        load_dotenv(env_path)
        api = OrderingAPI(True)
        return api

def test_Canceling_order_in_status_submitted(api_scenario):
    """
    # Test Case 2.1
    function that check the ability of canceled order in status 1
    :return: None
    """

    #stopped ordering_backgroundtasks service
    ordering_backgroundtasks = DockerManager()
    ordering_backgroundtasks.stop('eshop/ordering.backgroundtasks:linux-latest')
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
        # check if ordering send to basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id


    # check if after step 1 the status of order in db is really 1
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_1')) == order_status[0]['OrderStatusId']
    # send api request to cancel
    res=api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    ordering_backgroundtasks.start('eshop/ordering.backgroundtasks:linux-latest')
    sleep(20)
    print('Pass - test_Canceling_order_in_status_submitted')


def test_Canceling_order_in_status_awaiting(api_scenario):
    """
    # Test Case 2.2
    function that check the ability of canceled order in status 2
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
        # check if ordering send to basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id


        #excepted result : ordering->catalog(order start check if it is possible to create order)
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

    # send api request to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_Canceling_order_in_status_awaiting')




def test_Canceling_order_in_status_Stockconfirmed(api_scenario):
    """
    # Test Case 2.3
    function that check the ability of canceled order in status 3
    :return: None
    """


    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']


    #excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id


        #excepted result : ordering->catalog(order start check if it is possible to create order)
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
    # send api request to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_Canceling_order_in_status_Stockconfirmed')



def test_Canceling_order_in_status_paid(api_scenario):
    """
    # Test Case 2.4
    function that check the ability of canceled order in status 4
    :return: None
    """


    #send message to rabbitMQ->create new order , rabbitMQ->ordering
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

    # send api request to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('BAD_REQUEST'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 5
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print('Pass - test_Canceling_order_in_status_paid')



def test_Canceling_order_in_status_shipped(api_scenario):
    """
    # Test Case 2.5
    function that check the ability of canceled order in status 5
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
    # send api request to change status to shipped
    res=api_scenario.change_status_to_shipped(order_id)
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('order_status_shipped_event')
        assert mq.last_msg_body['OrderId'] == order_id
        # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    # waiting for the entity updated
    sleep(20)
    # send api request to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('BAD_REQUEST'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 5
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_5')) == order_status[0]['OrderStatusId']
    print('Pass - test_Canceling_order_in_status_shipped')



#--------------------------UPDATE ORDER STATUS TO SHIPPED -------------------------------------------------

def test_Update_order_from_submitted_to_shipped(api_scenario):
    """
    # Test Case 3.1 + 3.2
    function that check the ability of update status of order (1 to 5)
    :return: None
    """


    #stopped ordering_backgroundtasks service
    ordering_backgroundtasks = DockerManager()
    ordering_backgroundtasks.stop('eshop/ordering.backgroundtasks:linux-latest')
    #send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    #save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

        # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 1
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_1')) == order_status[0]['OrderStatusId']

    # send api request to change status to shipped
    res=api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('bad_request'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 1
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_1')) == order_status[0]['OrderStatusId']

    ordering_backgroundtasks.start('eshop/ordering.backgroundtasks:linux-latest')
    with RabbitMQ() as mq:
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
    # send api request to change status to shipped
    res = api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('bad_request'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']
    sleep(20)
    print('Pass - test_Update_order_from_submitted_to_shipped')

def test_Update_order_from_Stockconfirmed_to_shipped(api_scenario):
    """
    # Test Case 3.3
    function that check the ability of update status of order (3 to 5)
    :return: None
    """


    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
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
    # send api request to change status to shipped
    res = api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('bad_request'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']
    print('Pass - test_Update_order_from_Stockconfirmed_to_shipped')


def test_Update_order_from_paid_to_shipped(api_scenario):
    """
    # Test Case 3.4
    function that check the ability of update status of order (4 to 5)
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

    # send api request to change status to shipped
    res = api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('order_status_shipped_event')
        assert mq.last_msg_body['OrderId'] == order_id
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is change to 5
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_5')) == order_status[0]['OrderStatusId']
    print('Pass - test_Update_order_from_paid_to_shipped')



def test_Update_order_from_cancel_to_shipped(api_scenario):
    """
    # Test Case 3.5
    function that check the ability of update status of order (6 to 5)
    :return: None
    """


    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
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

    # send api request to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is really 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    # send api request to change status to shipped
    res=api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('BAD_REQUEST'))
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is stay 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_Update_order_from_cancel_to_shipped')


#-------------ORDER TRACKING-------------------------------------------------
def test_order_tracking_is_status_submit(api_scenario):
    """
    # Test Case 4.1 + 4.2
    function that : check the online tracking of order in status 1
    :return: None
    """

    # stopped ordering_backgroundtasks service
    ordering_backgroundtasks = DockerManager()
    ordering_backgroundtasks.stop('eshop/ordering.backgroundtasks:linux-latest')
    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STARTED_INTEGRATION_EVENT')
        assert mq.last_msg_body['UserId'] == os.getenv('USER_ID')

        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_SUBMITTED_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id

    # check if after step 1 the status of order in db is really 1
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_1')) == order_status[0]['OrderStatusId']

    # send api request to get order details
    res = api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    js=res.json()
    assert js['status'] == os.getenv('SUBMITTED')
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 1
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_1')) == order_status[0]['OrderStatusId']
    ordering_backgroundtasks.start('eshop/ordering.backgroundtasks:linux-latest')
    sleep(20)
    with RabbitMQ() as mq:
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

        # send api request to get order details
    res = api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    js = res.json()
    assert js['status'] == os.getenv('AWAITING_VALIDATION')
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 2
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_2')) == order_status[0]['OrderStatusId']
    print('Pass - test_order_tracking_is_status_submit')


def test_order_tracking_is_status_Stockconfirmed(api_scenario):
    """
    # Test Case 4.3
    function that : check the online tracking of order in status 3
    :return: None
    """


    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
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
    # send api request to get order details
    res = api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    js=res.json()
    assert js['status'] == os.getenv('STOCK_CONFIRMED')
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 3
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_3')) == order_status[0]['OrderStatusId']
    print('Pass - test_order_tracking_is_status_Stockconfirmed')



def test_order_tracking_is_status_paid(api_scenario):
    """
    # Test Case 4.4
    function that : check the online tracking of order in status 4
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

    # send api request to get order details
    res = api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    js=res.json()
    assert js['status'] == os.getenv('PAID')
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 4
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_4')) == order_status[0]['OrderStatusId']
    print('Pass - test_order_tracking_is_status_paid')



def test_order_tracking_is_status_shipped(api_scenario):
    """
    # Test Case 4.5
    function that : check the online tracking of order in status 5
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
    res=api_scenario.change_status_to_shipped(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        # check if ordering send to catalog simulator excepted message
        assert mq.last_msg_method.routing_key == os.getenv('order_status_shipped_event')
        assert mq.last_msg_body['OrderId'] == order_id
    # waiting for the entity updated
    sleep(20)
    # send api request to get order details
    res = api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('success'))
    js=res.json()
    assert js['status'] == os.getenv('SHIPPED')

    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 5
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_5')) == order_status[0]['OrderStatusId']
    print('Pass - test_order_tracking_is_status_shipped')



def test_order_tracking_is_status_cancel(api_scenario):
    """
    # Test Case 4.5
    function that : check the online tracking of order in status 6
    :return: None
    """

    # send message to rabbitMQ->create new order , rabbitMQ->ordering
    create_order(os.getenv('ALICE'))
    sleep(5)
    # save from DB the orderID of new entity order
    with MSSQLConnector() as conn:
        order_id = conn.select_query(os.getenv('SELECT_LAST_ENTITY_ORDERID'))
        order_id = order_id[0]['Id']

    # excepted result : ordering->basket(order start clear the basket)
    with RabbitMQ() as mq:
        mq.consume('Basket')
        # check if ordering send to basket simulator excepted message
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

    # send api request to change status to cancel
    res = api_scenario.cancel_order(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('SUCCESS'))
    with RabbitMQ() as mq:
        mq.consume('Ordering.signalrhub')
        assert mq.last_msg_method.routing_key == os.getenv('ORDER_STATUS_CANCEL_EVENT')
        assert mq.last_msg_body['OrderId'] == order_id
    # waiting for the entity updated
    sleep(20)
    # send api request to get order details
    res=api_scenario.get_order_by_id(order_id)
    # check the response code
    assert res.status_code == int(os.getenv('success'))
    js=res.json()
    assert js['status'] == os.getenv('CANCELLED')
    # waiting for the entity updated
    sleep(20)
    # check if after api response the status of order in db is 6
    with MSSQLConnector() as conn:
        order_status = conn.select_query(os.getenv('SELECT_STATUS').format(order_id))
        assert int(os.getenv('ORDER_STATUS_6')) == order_status[0]['OrderStatusId']
    print('Pass - test_order_tracking_is_status_cancel')









