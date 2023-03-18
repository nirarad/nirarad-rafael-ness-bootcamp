import json
import os
import time
import uuid
import time
import pytest
from utils.db.db_utils import MSSQLConnector
from utils.db import *
from utils.docker import docker_utils
from utils.rabbitmq.rabbitmq_events_messages import *
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_events_messages import SingleMessageConsumer
from dotenv import load_dotenv
import requests

load_dotenv()
@pytest.fixture(autouse=True)
def clean_rabbitmq_messages():
    # prepare something ahead of all tests
    with RabbitMQ() as mq:
        mq.clean_rabbit_messages()
@pytest.fixture(scope="session")
def api_alice():
    return OrderingAPI('alice','Pass123$')
@pytest.fixture(scope="session")
def api_bob():
    return OrderingAPI('bob','Pass123$')

#works
@pytest.mark.sanity
def test_create_order_success_flow():
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 1, Create new order success flow
    :return: passed/failed
    '''
    #creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Checking that the message of payment succeeded has been sent and
    #           checking that a message sent to catalog to update the stock
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.functional
def test_create_order_out_of_stock_failure_flow():
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 2, Create an order with out of stock flow
    :return: Pass/Failed
    '''

    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending message that there are not enough products in stock and checking that the message has arrived
    # Order status id = 6
    reject_stock(order_id)
   # catalog.wait_for_message()
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#works
@pytest.mark.functional
def test_create_order_with_payment_failure():
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 3, Create new order with payment failure
    :return: passed/failed
    '''
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))
    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    confirm_stock(order_id)
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
    order_payment_failed_integration_event(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    #assert payment.last_msg_method.routing_key == os.getenv('routing_key_fail')
    # checking if the status id in the DB equals to the expected result after the proccess of sending payment failed message
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#works
@pytest.mark.functional
def test_create_an_order_with_Quantity_0():
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 4, Check the creation of a new order when the Quantity =0
    :return: passed/failed
    '''
    last_id = MSSQLConnector().get_last_id()
    # creation of a new order
    create_order_without_quantity()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    # Checking that a new row did not add to the db
    assert  MSSQLConnector().get_last_id() == last_id
#works
@pytest.mark.functional
def test_create_an_order_without_items_in_the_basket():
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 5, Check the creation of a new order when basket is empty
    :return:passed/failed
    '''
    last_id = MSSQLConnector().get_last_id()
    # creation of a new order
    create_order_without_items()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    # Checking that a new row did not add to the db
    assert MSSQLConnector().get_last_id() == last_id
#works
@pytest.mark.sanity
def test_update_order_success_flow(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 6, Check the update of an order from  status 4 to 5
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')

    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_five'))
#works
@pytest.mark.functional
def test_update_order_failure_flow_1(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 7, Check the update of an order from  status 1 to 5
    :param api_alice: a connection of the user alice
    :return: passed/failed
    '''
    # Stopping backgroundtasks for stuck the status id on 1
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    order_id = MSSQLConnector().get_last_id()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))
    time.sleep(int(os.getenv('sleep_time')))
    dm.start('eshop/ordering.backgroundtasks:linux-latest')
#works
@pytest.mark.functional
def test_update_order_failure_flow_2(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 8, Check the update of an order from  status 2 to 5
    :param api_alice: a connection of the user alice
    :return:
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')

    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))
#works
@pytest.mark.functional
def test_update_order_failure_flow_3(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 9, Check the update of an order from  status 3 to 5
    :param api_alice: a connection of the user alice
    :return:
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')

    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
#works
@pytest.mark.functional
def test_update_order_failure_flow_4(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 10, Check the update of an order from  status 6 to 5
    :param api_alice: a connection of the user alice
    :return: passed/failed
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending message that there are not enough products in stock and checking that the message has arrived
    # Order status id = 6
    reject_stock(order_id)
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#works
@pytest.mark.sanity
def test_cancel_order_success_1(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 11, Check the cancel of an order from status 1 to 6
    :param api_alice: a connection of the user alice
    :return: passed/failed
    '''
    # Stopping backgroundtasks for stuck the status id on 1
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    order_id = MSSQLConnector().get_last_id()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
    dm.start('eshop/ordering.backgroundtasks:linux-latest')
#works
@pytest.mark.functional
def test_cancel_order_success_2(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 12, Check the cancel of an order from status 2 to 6
    :param api_alice: a connection of the user alice
    :return: passed/failed
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#works
@pytest.mark.functional
def test_cancel_order_success_3(api_alice):
    '''
    Writer:Or David
    Date:14/03/23
    Test case number 13, Check the cancel of an order from status 3 to 6
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''
    # creation of a new order
    create_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    confirm_stock(order_id)
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
    payment = SingleMessageConsumer('Payment')
    order_payment_failed_integration_event(order_id)
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#works
@pytest.mark.functional
def test_cancel_order_failure_1(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 14, Check the cancel of an order from status 4 to 6
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_AWAITING_VALIDATION')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))
#works
@pytest.mark.functional
def test_cancel_order_failure_2(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 15, Check the cancel of an order from status 5 to 6
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_five'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
   # api_alice.cancel_order(order_id)
    #assert api_alice.status_code() == 400
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_five'))
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_1(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 16, Check that the order with status 1 is trackable
    :param api_alice: a connection of the user alice
    :return: Pass/Failed
    '''
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    order_id = MSSQLConnector().get_last_id()
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))
    dm.start('eshop/ordering.backgroundtasks:linux-latest')
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_2(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 17, Check that the order with status 2 is trackable
    :param api_alice: a connection of the user alice
    :return: Passed/Failed
    '''
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_3(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 18 Check that the order with status 3 is trackable
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_4(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 19 Check that the order with status 4 is trackable
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_5(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 20 Check that the order with status 5 is trackable
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_five'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_five'))
#works
@pytest.mark.functional
def test_track_of_an_order_success_flow_6(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 21 Check that the order with status 6 is trackable
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_six'))
#bug - status code 200 instead of 400
@pytest.mark.security
def test_authentication_success_flow_1(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 22 ,Check that the user cannot send a get request to an order by id of another user
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a GET(orderId) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
#works
@pytest.mark.security
def test_authentication_success_flow_2(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 23 ,Check that the user cannot send a get request to an orders of another user
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a GET(orders) message to Ordering and checking status code and status id
    response = api_alice.get_orders()
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
#bug - bug update to 5 instead of 4, status code 200 instead of 400
@pytest.mark.security
def test_authentication_success_flow_3(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 24 ,Check that the user cannot send a put request(ship) to an order of another user
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.security
def test_authentication_success_flow_4(api_alice):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 25 ,Check that the user cannot send a put request(cancel) to an order of another user
    :param api_alice: a connection of the user alice
    :return:passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))


    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))
#works
@pytest.mark.failure_recovery
def test_system_recovery_success_flow_1():
    '''
    Writer:Or david
    Date:09/03/23
    Test case number 27 Check System recovery success flow 1
    :return:passed/failed
    '''

    # backgroundtasks turn off
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    order_id = MSSQLConnector().get_last_id()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_one'))

    # backgroundtasks turn on
    dm.start('eshop/ordering.backgroundtasks:linux-latest')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.failure_recovery
def test_system_recovery_success_flow_2():
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 28 Check the recovery of the system after crash from status 2
    :return:pass /failed
    '''
    dm = docker_utils.DockerManager()
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Ordering turn off
    dm.stop('eshop/ordering.api:linux-latest')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    confirm_stock(order_id)
    time.sleep(int(os.getenv('long_sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Ordering turn on
    dm.start('eshop/ordering.api:linux-latest')
    time.sleep(int(os.getenv('long_sleep_time')))

    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('long_sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.failure_recovery
def test_system_recovery_success_flow_3():
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 29 Check the recovery of the system after crash from status 3
    :return:passed/failed
    '''
    dm = docker_utils.DockerManager()
    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # ordering turn off
    dm.stop('eshop/ordering.api:linux-latest')
    time.sleep(int(os.getenv('long_sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    payment_succeeded(order_id)  # unable to send

    # still on status 3
    time.sleep(int(os.getenv('long_sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # ordering turn on
    dm.start('eshop/ordering.api:linux-latest')

    time.sleep(int(os.getenv('long_sleep_time')))
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#works
@pytest.mark.security
def test_authentication_success_flow_1_bob_user(api_bob):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 30 , Check that the user(bob) cannot send a get request to an order of another user (alice)
    :param api_bob: a connection of the user bob
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))


    # Sending a GET(orderId) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_bob.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
#works
@pytest.mark.security
def test_authentication_success_flow_2_bob_user(api_bob):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 31 ,Check that the user(bob) cannot send a get orders request to an order of another user (alice)
    :param api_bob: a connection of the user bob
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))


    # Sending a GET(orders) message to Ordering and checking status code and status id
    response = api_bob.get_orders()
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
#bug failed 200 == 400
@pytest.mark.security
def test_authentication_success_flow_3_bob_user(api_bob):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 32 ,Check that the user(bob) cannot send a put(ship) request to an order of another user (alice)
    :param api_bob: a connection of the user bob
    :return:passed/failed
    '''

    # Creation of a new order
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    confirm_stock(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_bob.change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))
#bug - failed 200==400
@pytest.mark.security
def test_authentication_success_flow_4_bob_user(api_bob):
    '''
    Writer:Or David
    Date:09/03/23
    Test case number 33 ,Check that the user(bob) cannot send a put(cancel) request to an order of another user (alice)
    :param api_bob: a connection of the user bob
    :return:passed/failed
    '''

    # Creation of a new order of alice user (by default)
    create_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

    # Checking that the message of checking enough products in stock has arrived in the catalog
    # Order status id = 2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_bob.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))
#bug
@pytest.mark.scalability
def test_create_100_orders():
    '''
    Writer:Or david
    Date:09/03/23
    Test case number 26, Create 100 orders less than 1 hour
    :return:passed/failed
    '''
    start_time = time.time()
    # Creation of a new order
    for i in range(100):
        create_order()
           # time.sleep(os.getenv('sleep_time))
        # Checking the message sending after step 1 of start integration
        # Order status id =1
        basket = SingleMessageConsumer('Basket')
        basket.wait_for_message()
        assert basket.last_msg_method.routing_key == os.getenv('routing_key_submit')

        # Checking that the message of checking enough products in stock has arrived in the catalog
        # Order status id = 2
        catalog = SingleMessageConsumer('Catalog')
        catalog.wait_for_message()
        assert catalog.last_msg_method.routing_key == os.getenv('routing_key_awaiting_validation')
        order_id = catalog.last_msg_body['OrderId']
        time.sleep(int(os.getenv('sleep_time')))
        assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_two'))

        # Sending message that there are enough products in stock and checking that the message has arrived
        # Order status id = 3
        confirm_stock(order_id)
        payment = SingleMessageConsumer('Payment')
        payment.wait_for_message()
        assert payment.last_msg_method.routing_key == os.getenv('routing_key_stock_confirmed')
        time.sleep(int(os.getenv('sleep_time')))
        assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_three'))

        # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
        # Order status id = 4
        payment_succeeded(order_id)
        catalog.wait_for_message()
        assert catalog.last_msg_method.routing_key == os.getenv('routing_key_paid')
        time.sleep(int(os.getenv('sleep_time')))
        assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('status_id_four'))

    end_time = time.time()
    elapsed_time = end_time - start_time
    assert elapsed_time < 3600  # Check that the elapsed time is less than 1 hour






