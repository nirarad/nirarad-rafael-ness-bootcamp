import os
import time
import pytest
from tests.singleMassage import SingleMessageConsumer
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker import docker_utils
from utils.rabbitmq.rabbitmq_messages import create_new_order, order_stock_confirmed, order_payment_succeeded, \
    order_stock_reject, payment_failed, \
    create_order_quantity_0, create_order_without_items, create_new_order_bob
from dotenv import load_dotenv
from utils.rabbitmq.rabbitmq_send import RabbitMQ
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

@pytest.mark.sanity
def test_create_order_success():
    '''
    Writer:Romi Segal
    Date: 09/03/23
    Test case number 1, MSS-Create new order success flow
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock
    # in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.functional
def test_create_order_out_of_stock():
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 2, Create an order without of stock flow
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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


    # Checking if the status id in the DB equals to the expected result after the proccess of sending reject message
    order_stock_reject(order_id)
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.functional
def test_create_order_with_quantity_0():
    '''
    Writer:Romi Segal
    Date:14/03/23
    Test case number 3, Create new order with quantity=0
    param: None
    return: passed/failed
    '''

    last_id = MSSQLConnector().select_last_id()
    # Creation of a new order
    create_order_quantity_0()
    # Checking the message sending after step 1 of start integration
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    # Checking that a new row did not add to the db
    assert MSSQLConnector().select_last_id() == last_id

@pytest.mark.functional
def test_create_order_without_items():
    '''
    Writer:Romi Segal
    Date:14/03/23
    Test case number 4, Create new order without items in the basket
    param: None
    return: passed/failed
    '''

    last_id = MSSQLConnector().select_last_id()
    # Creation of a new order
    create_order_without_items()
    # Checking the message sending after step 1 of start integration
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    # Checking that a new row did not add to the db
    assert MSSQLConnector().select_last_id() == last_id

@pytest.mark.functional
def test_create_order_with_payment_failure():
    '''
    Writer:Romi Segal
    Date:14/03/23
    Test case number 5, Create new order with payment failure
    param: None
    return: passed/failed
    '''
    # Creation of a new order
    create_new_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')

    # checking the message sending after step 1 if there are enough products in stock has arrived in the catalog
    # Order status id =2
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_AWAITING_VALIDATION')
    order_id = catalog.last_msg_body['OrderId']
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))
    # Sending message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    order_stock_confirmed(order_id)
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))
    payment_failed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    #assert payment.last_msg_method.routing_key == os.getenv('routing_key_fail')
    # checking if the status id in the DB equals to the expected result after the proccess of sending payment failed message
    time.sleep(int(os.getenv('sleep_time')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.sanity
def test_update_order_success(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 6, Check the update of an order from  status 4 to 5
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock
    # in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FIVE'))

@pytest.mark.functional
def test_update_order_failure_flow_1(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 7, Check the update of an order from  status 1 to 5
    param: None
    return: passed/failed
    '''

    # Stopping backgroundtasks for stuck the status id on 1
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # creation of a new order
    create_new_order()
    # checking the message sending after step 1 of start integration
    # Order status id = 1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    order_id = MSSQLConnector().select_last_id()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))

    dm.start('eshop/ordering.backgroundtasks:linux-latest')

@pytest.mark.functional
def test_update_order_failure_flow_2(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 8, Check the update of an order from  status 2 to 5
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

@pytest.mark.functional
def test_update_order_failure_flow_3(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 9, Check the update of an order from  status 3 to 5
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

@pytest.mark.functional
def test_update_order_failure_flow_4(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 10, Check the update of an order from status 6 to 5
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Checking if the status id in the DB equals to the expected result after the proccess of sending reject message
    order_stock_reject(order_id)
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.sanity
def test_cancel_order_success_1(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 11, Check the cancel of an order from status 1 to 6
    param: None
    return: passed/failed
    '''
    dm = docker_utils.DockerManager()
    # backgroundtasks turn off
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # Creation of a new order
    create_new_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    order_id = MSSQLConnector().select_last_id()
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))
    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))
    # backgroundtasks turn on
    dm.start('eshop/ordering.backgroundtasks:linux-latest')

@pytest.mark.functional
def test_cancel_order_success_2(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 12, Check the cancel of an order from status 2 to 6
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.functional
def test_cancel_order_success_3(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 13, Check the cancel of an order from status 3 to 6
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.functional
def test_cancel_order_failure_1(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 14, Check the cancel of an order from status 4 to 6
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.functional
def test_cancel_order_failure_2(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 15, Check the cancel of an order from status 5 to 6
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FIVE'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FIVE'))

@pytest.mark.functional
def test_track_of_an_order_success_flow_1(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 16 Check the track of an order 1
    param: None
    return: passed/failed
    '''

    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # Creation of a new order
    create_new_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    order_id = MSSQLConnector().select_last_id()
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))

    dm.start('eshop/ordering.backgroundtasks:linux-latest')

@pytest.mark.functional
def test_track_of_an_order_success_flow_2(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 17 Check the track of an order 2
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

@pytest.mark.functional
def test_track_of_an_order_success_flow_3(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 18 Check the track of an order 3
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

@pytest.mark.functional
def test_track_of_an_order_success_flow_4(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 19 Check the track of an order 4
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.functional
def test_track_of_an_order_success_flow_5(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 20 Check the track of an order 5
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FIVE'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FIVE'))

@pytest.mark.functional
def test_track_of_an_order_success_flow_6(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 21 Check the track of an order 6
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

    # Sending a GET(orderid) message to Ordering and checking status code
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_SIX'))

@pytest.mark.security
def test_authentication_success_flow_1(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 22 ,Check that the user cannot send a get request to an order by id of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
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


    # Sending a GET(orderId) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400')) #bug

@pytest.mark.security
def test_authentication_success_flow_2(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 23 ,Check that the user cannot send a get request to an orders of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
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


    # Sending a GET(orders) message to Ordering and checking status code and status id
    response = api_alice.get_orders()
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))

@pytest.mark.security
def test_authentication_success_flow_3(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 24 ,Check that the user cannot send a update request to an order of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_alice.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))#bug
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.security
def test_authentication_success_flow_4(api_alice):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 25 ,Check that the user cannot send a cancel request to an order of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order_bob()
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
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_alice.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400'))#bug
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

@pytest.mark.security
def test_authentication_success_flow_1_bob(api_bob):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 26 ,Check that the user cannot send a get request to an order by id of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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


    # Sending a GET(orderId) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_bob.get_order_by_id(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400')) #bug

@pytest.mark.security
def test_authentication_success_flow_2_bob(api_bob):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 27 ,Check that the user cannot send a get request to an orders of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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


    # Sending a GET(orders) message to Ordering and checking status code and status id
    response = api_bob.get_orders()
    assert response.status_code == int(os.getenv('STATUS_CODE_200'))

@pytest.mark.security
def test_authentication_success_flow_3_bob(api_bob):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 28 ,Check that the user cannot send update request to an order of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    # Sending a PUT(ship) message to Ordering and checking status code and status id
    # Order status id = 5
    response = api_bob.put_change_status_to_shipped(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400')) #bug
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.security
def test_authentication_success_flow_4_bob(api_bob):
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 29 ,Check that the user cannot send a cancel request to an order of another user
    param: None
    return: passed/failed
    '''

    # Creation of a new order
    create_new_order()
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
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Sending a PUT(cancel) message to Ordering and checking status code and status id
    response = api_bob.cancel_order(order_id)
    assert response.status_code == int(os.getenv('STATUS_CODE_400')) #bug
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

@pytest.mark.scalability
def test_create_100_orders():
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 30, Create 100 orders less than 1 hour
    param: None
    return: passed/failed
    '''

    start_time = time.time()

    # Creation of a new order
    for i in range(100):
        time.sleep(15)
        create_new_order()
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

        # Sending message that there are enough products in stock and checking that the message has arrived
        # Order status id = 3
        order_stock_confirmed(order_id)
        payment = SingleMessageConsumer('Payment')
        payment.wait_for_message()
        assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
        time.sleep(int(os.getenv('SLEEP_TIME')))
        assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

        # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
        # Order status id = 4
        order_payment_succeeded(order_id)
        catalog.wait_for_message()
        assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
        time.sleep(int(os.getenv('SLEEP_TIME')))
        assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

    end_time = time.time()
    elapsed_time = end_time - start_time
    assert elapsed_time < 3600  # Check that the elapsed time is less than 1 hour

@pytest.mark.failure_recovery
def test_system_recovery_success_flow_1():
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 31 Check System recovery success flow 1
    param: None
    return: passed/failed
    '''

    #backgroundtasks turn off
    dm = docker_utils.DockerManager()
    dm.stop('eshop/ordering.backgroundtasks:linux-latest')
    # Creation of a new order
    create_new_order()
    # Checking the message sending after step 1 of start integration
    # Order status id =1
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    order_id = MSSQLConnector().select_last_id()
    assert basket.last_msg_method.routing_key == os.getenv('ROUTING_KEY_SUBMIT')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_ONE'))

    # backgroundtasks turn on
    dm.start('eshop/ordering.backgroundtasks:linux-latest')

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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.failure_recovery
def test_system_recovery_success_flow_2():
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 32 Check the recovery of the system after crash from status 2
    param: None
    return: passed/failed
    '''

    dm = docker_utils.DockerManager()
    # Creation of a new order
    create_new_order()
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
    time.sleep(int(os.getenv('LONG_TIME_SLEEP')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Ordering turn off
    dm.stop('eshop/ordering.api:linux-latest')

    time.sleep(int(os.getenv('LONG_TIME_SLEEP')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Sending a message that there are enough products in stock and checking that the message has arrived
    # Order status id = 3
    order_id = catalog.last_msg_body['OrderId']
    order_stock_confirmed(order_id)
    time.sleep(int(os.getenv('LONG_TIME_SLEEP')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_TWO'))

    # Ordering turn on
    dm.start('eshop/ordering.api:linux-latest')

    time.sleep(int(os.getenv('LONG_TIME_SLEEP')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    # Order status id = 4
    order_payment_succeeded(order_id)
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))

@pytest.mark.failure_recovery
def test_system_recovery_success_flow_3():
    '''
    Writer:Romi Segal
    Date:09/03/23
    Test case number 33 Check the recovery of the system after crash from status 3 to 4
    param: None
    return: passed/failed
    '''

    dm = docker_utils.DockerManager()
    # Creation of a new order
    create_new_order()
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
    order_stock_confirmed(order_id)
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == os.getenv('ROUTING_KEY_STOCK_CONFIRMED')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # ordering turn off
    dm.stop('eshop/ordering.api:linux-latest')
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    # Sending a message that the payment has been made and checking a message that the stock in the catalog has been updated
    order_payment_succeeded(order_id) # unable to send

    #still on status 3
    time.sleep(int(os.getenv('SLEEP_TIME')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_THREE'))

    #ordering turn on
    dm.start('eshop/ordering.api:linux-latest')

    time.sleep(int(os.getenv('LONG_TIME_SLEEP')))
    assert MSSQLConnector().orderStatusid(order_id) == int(os.getenv('STATUS_ID_FOUR'))
    assert catalog.last_msg_method.routing_key == os.getenv('ROUTING_KEY_PAID')








