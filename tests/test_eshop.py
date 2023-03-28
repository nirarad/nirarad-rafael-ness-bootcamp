import pytest
import time
import os

from dotenv import load_dotenv

from utils.api.ordering_api import OrderingAPI
from utils.db.db_query import last_order_id, last_order_status
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_receive import *

from simulator.basket import *
from simulator.payment import *
from simulator.catalog import *

from time import sleep


@pytest.fixture(autouse=True)
def eShop():
    load_dotenv()
    with RabbitMQ() as MQ:
        MQ.purge_all()


@pytest.mark.sanity
def test_create_order():
    '''
    Test the creation of a new order (MSS)
    '''

    # Create a new order.
    create_order()
    # Basket receives a message, the status in the DB 1
    assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
    # Catalog receives a message, the status in the DB changes to 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB changes to 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == \
           int(os.getenv('STATUS_STOCKCONFIRMED'))
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status in the DB changes to 4
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_PAID'))

def test_hundred_orders_per_hour():
    """
    Test checks whether the system is capable of closing 100 orders within an hour.
    """
    start_time = time.time()
    for i in range(3):
        # Create a new order.
        create_order()
        # Basket receives a message, the status in the DB 1
        assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
        assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
        # Catalog receives a message, the status in the DB changes to 2
        assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
        assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
        # Message The item is in stock
        in_stock(last_order_id())
        # Payment receives a message, the status in the DB changes to 3
        assert Receive_message_from_queue(
            'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == \
               int(os.getenv('STATUS_STOCKCONFIRMED'))
        # Message The payment was made successfully
        payment_success(last_order_id())
        # Catalog receives a message, the status in the DB changes to 4
        assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
        assert last_order_status() == int(os.getenv('STATUS_PAID'))
    end_time = time.time()
    duration = end_time - start_time
    assert duration < 3600

def test_ship_another_user():
    """
    Test that checks that it is not possible to send a shipment for another user's order
    """
    # Create a new order with another user.
    create_order_bob()
    # Catalog receives a message
    Receive_message_from_queue('Catalog')
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message
    Receive_message_from_queue('Payment')
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message
    Receive_message_from_queue('Catalog')
    # Message the shipment has been made, status code 401
    statuscode = OrderingAPI().status_shipped(last_order_id()).status_code
    assert statuscode == int(os.getenv('STATUS_CODE_UNAUTHORIZED'))


def test_get_orders():
    """
    Test checks that status code 200 If he returns orders
    """
    status_code = OrderingAPI().get_orders().status_code
    assert status_code == int(os.getenv('STATUS_CODE_SUCCESS'))


def test_get_order_by_id():
    """
    Test checks that status code 200 If he returns order by id
    """
    status_code = OrderingAPI().get_order_id(100).status_code
    assert status_code == int(os.getenv('STATUS_CODE_SUCCESS'))


def test_get_card_type():
    """
    Test checks that status code 200 If he returns type card
    """
    status_code = OrderingAPI().get_card_type().status_code
    assert status_code == int(os.getenv('STATUS_CODE_SUCCESS'))


def test_cancel_status_1():
    '''
    test that cancels with status 1
    '''

    # Create a new order.
    create_order()
    # Basket receives a message, the status in the DB 1
    assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
    # Pause the ordering background task container.
    dm = DockerManager()
    if dm.check_status('eshop/ordering.backgroundtasks:linux-latest') == 'running':
        dm.pause('eshop/ordering.backgroundtasks:linux-latest')
    assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
    # Cancel the last order.
    OrderingAPI().cancel_order(last_order_id())
    # Unpause the ordering background task container.
    dm.unpause('eshop/ordering.backgroundtasks:linux-latest')
    # Assert that the last order has status 4 in DB.
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))


def test_cancel_status_2():
    '''
    test that cancels with status 2
    '''

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    sleep(5)
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Cancel the last order.
    OrderingAPI().cancel_order(last_order_id())
    # Assert that the last order has status 4 in DB.
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))


def test_cancel_status_3():
    '''
    test that cancels with status 3
    '''

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB changes to 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # Cancel the last order.
    OrderingAPI().cancel_order(last_order_id())
    # Assert that the last order has status 4 in DB.
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))


def test_cancel_status_4_negative(eShop):
    '''
    test that cancels with status 4(Negative)
    '''
    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB changes to 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status in the DB changes to 4
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_PAID'))
    # Cancel the last order.
    statusCode = OrderingAPI().cancel_order(last_order_id()).status_code
    # Assert to receive status code 400 and that the status will remain 4
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_PAID'))


def test_cancel_status_5_negative():
    '''
    test that cancels with status 5(Negative)
    '''

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB changes to 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status in the DB changes to 4
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_PAID'))
    # purge messages in queue Webhooks
    with RabbitMQ() as MQ:
        MQ.purge('Webhooks')
    # Message the shipment has been made
    OrderingAPI().status_shipped(last_order_id())
    # Webhooks receives a message, the status in the DB changes to 5
    assert Receive_message_from_queue('Webhooks') == 'OrderStatusChangedToShippedIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_SHIPPED'))
    # Cancel the last order.
    statusCode = OrderingAPI().cancel_order(last_order_id()).status_code
    # Assert to receive status code 400 and that the status will remain 5
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_SHIPPED'))


def test_ship_status_1_negative():
    '''
     test that updates to status 'shipped' when in status 1 (Negative)
    '''

    # Create a new order.
    create_order()
    # Basket receives a message, the status in the DB 1
    assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
    # Pause the ordering background task container.
    dm = DockerManager()
    if dm.check_status('eshop/ordering.backgroundtasks:linux-latest') == 'running':
        dm.pause('eshop/ordering.backgroundtasks:linux-latest')
    assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
    # Message the shipment has been made
    statusCode = OrderingAPI().status_shipped(last_order_id()).status_code
    # Unpause the ordering background task container.
    dm.unpause('eshop/ordering.backgroundtasks:linux-latest')
    # Assert to receive status code 400 and that the status will remain 1
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_SUBMITTED'))


def test_ship_status_2_negative():
    """
    test that updates to status 'shipped' when in status 2 (Negative)
    """

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    sleep(5)
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message the shipment has been made
    statusCode = OrderingAPI().status_shipped(last_order_id()).status_code
    # Assert to receive status code 400 and that the status will remain 2
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_AWAITINGVALIDATION'))


def test_ship_status_3_negative():
    """
    test that updates to status 'shipped' when in status 3 (Negative)
    """

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # Message the shipment has been made
    statusCode = OrderingAPI().status_shipped(last_order_id()).status_code
    # Assert to receive status code 400 and that the status will remain 3
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))


def test_ship_status_4():
    """
    test that updates to status 'shipped' when in status 4
    """

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == \
           int(os.getenv('STATUS_STOCKCONFIRMED'))
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status in the DB changes to 4
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_PAID'))
    # purge messages in queue Webhooks
    with RabbitMQ() as MQ:
        MQ.purge('Webhooks')
    # Message the shipment has been made
    OrderingAPI().status_shipped(last_order_id())
    # Webhooks receives a message, the status in the DB 5
    assert Receive_message_from_queue('Webhooks') == 'OrderStatusChangedToShippedIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_SHIPPED'))


def test_ship_status_6_negative():
    """
    test that updates to status 'shipped' when in status 6 (Negative)
    """

    # Create a new order.
    create_order()
    # Basket receives a message, the status in the DB 1
    assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
    # Cancel the last order.
    OrderingAPI().cancel_order(last_order_id())
    # the status in the DB 6
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))
    # Message the shipment has been made
    statusCode = OrderingAPI().status_shipped(last_order_id()).status_code
    # Assert to receive status code 400 and that the status will remain 3
    assert statusCode == int(os.getenv('STATUS_CODE_BAD_REQUEST')) and last_order_status() == int(
        os.getenv('STATUS_CANCELLED'))


def test_payment_succeeded():
    """
    test that the payment was successful
    """

    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status in the DB 4
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToPaidIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_PAID'))


def test_payment_failed():
    """
    Test that payment has failed
    """
    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))
    # purge messages in queue Ordering.signalrhub
    with RabbitMQ() as MQ:
        MQ.purge('Ordering.signalrhub')
    # Message The payment was failed
    payment_failed(last_order_id())
    # Ordering.signalrhub receives a message, the status in the DB 6
    assert Receive_message_from_queue('Ordering.signalrhub') == 'OrderStatusChangedToCancelledIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))


def test_confirm_stock():
    """
    test that checks if the inventory exists
    """
    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status in the DB 3
    assert Receive_message_from_queue(
        'Payment') == 'OrderStatusChangedToStockConfirmedIntegrationEvent' and last_order_status() == int(
        os.getenv('STATUS_STOCKCONFIRMED'))


def test_reject_stock():
    """
    Test that checks if the inventory does not exist.
    """
    # Create a new order.
    create_order()
    # Catalog receives a message, the status in the DB 2
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_AWAITINGVALIDATION'))
    # Message The item is not in stock
    not_in_stock(last_order_id())
    sleep(30)
    # the status in the DB 6
    assert last_order_status() == int(os.getenv('STATUS_CANCELLED'))


def test_order_tracking():
    """
    test that checks that the statuses change according to the step where the user is at
    """
    # Create a new order.
    create_order()
    # Basket receives a message, the status submitted
    Receive_message_from_queue('Basket')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'submitted'
    # Catalog receives a message, the status awaitingvalidation
    Receive_message_from_queue('Catalog')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'awaitingvalidation'
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, the status stockconfirmed
    Receive_message_from_queue('Payment')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'stockconfirmed'
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, the status paid
    Receive_message_from_queue('Catalog')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'paid'


def test_Cancel_another_user():
    '''
    Test that checks that it is not possible to cancel an order of another user.
    '''

    # Create a new order with another user.
    create_order_bob()
    # Basket receives a message, the status in the DB 1
    assert Receive_message_from_queue('Basket') == 'OrderStartedIntegrationEvent'
    assert last_order_status() == int(os.getenv('STATUS_SUBMITTED'))
    # Cancel the last order, status code 401.
    statuscode = OrderingAPI().cancel_order(last_order_id()).status_code
    assert statuscode == int(os.getenv('STATUS_CODE_UNAUTHORIZED'))


def test_payment_another_user():
    """
    Test that verifies that it's impossible to pay for an order of another user.
    """
    # Create a new order with another user.
    create_order_bob()
    # Catalog receives a message
    assert Receive_message_from_queue('Catalog') == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message
    Receive_message_from_queue('Payment')
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message
    Receive_message_from_queue('Catalog')
    # status in the DB != 4
    assert last_order_status() != int(os.getenv('STATUS_PAID'))


def test_crash_ordering_service():
    """
    Test that checks if the system returns to the same place it stopped after a crash.
    """
    # Create a new order
    create_order()
    # Basket receives a message, status submitted
    Receive_message_from_queue('Basket')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'submitted'
    # Catalog receives a message, status awaitingvalidation
    Receive_message_from_queue('Catalog')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'awaitingvalidation'
    # Pause the ordering API task container.
    dm = DockerManager()
    if dm.check_status('eshop/ordering.api:linux-latest') == 'running':
        dm.pause('eshop/ordering.api:linux-latest')
    # Unpause the ordering API task container.
    dm.unpause('eshop/ordering.api:linux-latest')
    # Message The item is in stock
    in_stock(last_order_id())
    # Payment receives a message, status stockconfirmed
    Receive_message_from_queue('Payment')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'stockconfirmed'
    # Pause the ordering API task container.
    if dm.check_status('eshop/ordering.api:linux-latest') == 'running':
        dm.pause('eshop/ordering.api:linux-latest')
    # Unpause the ordering API task container.
    dm.unpause('eshop/ordering.api:linux-latest')
    # Message The payment was made successfully
    payment_success(last_order_id())
    # Catalog receives a message, status paid
    Receive_message_from_queue('Catalog')
    assert OrderingAPI().get_order_id(last_order_id()).json()['status'] == 'paid'





if __name__ == '__main__':
    pytest.main()
