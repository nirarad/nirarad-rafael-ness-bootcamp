import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.Api.ordering_api import OrderingAPI
from Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from Utils.DB.db_functions import *


######################################################################################################################################################################################
##################################### -------------Load and Reliability Tests-----------------------############################################################################
######################################################################################################################################################################################

def test_ordering_process_over_hour(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Testing Reliability and Scalability of UUT, running a number of orders per hour.

    """
    orders_count_prior = select_orders_count()

    starting_time = time.time()

    for _ in range(int(os.getenv('RELIABILITY_TEST_COUNTER'))):
        # Preconditions - OrderingBackground down

        docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    # Step 1: Create an order and remove items from the basket, ensure entity is created in db, and status changed to '1' = Submitted.
        
        basket.send_new_order()
        
        assert basket.received_remove_basket() is True
        assert verify_latest_order_status_id(
            int(os.getenv('SUBMITTED_STATUS')))

    # Step 2: Start the ordering background service, ensure status = '2' - Awaiting Validation.
        
        order_id = select_last_order()['Id']
        docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

        assert catalog.received_check_stock() is True
        assert verify_latest_order_status_id(
            int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3: Confirm the item inventory and status changed to '3' - Confirmed.
        
        catalog.send_valid_stock(order_id)
        assert verify_latest_order_status_id(
            int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4: Verify that the order status is set to '4' - Paid.
        
        assert payment.received_stock_confirmed() is True
        payment.send_confirmed_payment(order_id)
        assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

        with RabbitMQ() as mq:
            mq.purge_all()

    # Step 5: Ensure the tests are run at 1 hour

    assert (select_orders_count() -
            orders_count_prior) == int(os.getenv('RELIABILITY_TEST_COUNTER'))
    assert time.time() - starting_time == timedelta(hours=1)

######################################################################################################################################################################################
##################################### -------------Survivability and Recovery Tests-----------------------############################################################################
######################################################################################################################################################################################


def test_ordering_service_after_crash(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Tests system behavior when the UUT crashes
    before each step of the order process.
    Verifies system recovery, data integrity and continuation to next step.  

    """
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    # Step 1
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    basket.send_new_order()

    assert basket.received_remove_basket() is True
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    assert payment.received_stock_confirmed() is True

    # Step 5
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    payment.send_confirmed_payment(order_id)
    assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

    # Step 6
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    ordering_api.ship_order(order_id)
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


######################################################################################################################################################################################
##################################### -------------Security Tests-----------------------############################################################################################
######################################################################################################################################################################################

def test_cancel_other_user_order(ordering_api: OrderingAPI):
    assert ordering_api.cancel_order(int(os.getenv('BOB_ORDER_ID'))).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))


def test_ship_others_user_order(ordering_api: OrderingAPI):
    assert ordering_api.ship_order(int(os.getenv('BOB_ORDER_ID'))).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))


def test_accessing_orders_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_all_orders().status_code == int(
        os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_get_order_by_id_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_order_by_id(1).status_code == int(
        os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_card_types_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_cardtypes().status_code == int(
        os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_ship_order_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.ship_order(1).status_code == int(
        os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_cancel_order_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.cancel_order(1).status_code == int(
        os.getenv('UNAUTHORIZED_RESPONSE_CODE'))
