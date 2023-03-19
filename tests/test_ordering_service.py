import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.DB.db_functions import *


######################################################################################################################################################################################
##################################### --------------------------Functional Tests-----------------------################################################################################
######################################################################################################################################################################################


######################################################################################################################################################################################
##################################### --------------------------Sanity-----------------------#########################################################################################
######################################################################################################################################################################################

# MSS
def test_mss_scenario(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Test the complete sucssesful order creation scenario.

    """
    # Preconditions - OrderingBackground down
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    prior_count = select_orders_count()

    # Step 1: Create an order and remove items from the basket, ensure entity is created in db, and status changed to '1' = Submitted.
    basket.send_new_order()

    assert basket.received_remove_basket() is True

    assert prior_count < select_orders_count()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

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


def test_ordering_items_outOfStock(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock):
    """
    Test the order creation process with out-of-stock items in order.

    """
    # Preconditions - OrderingBackground down
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    # Step 1: Create an order and remove items from the basket, ensure entity is created in db.
    basket.send_new_order()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2: Start the ordering background service, ensure status = '2' and verify the items are in stock.
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3: Ensure that when items aren't in stock, order status is set to "6" - cancelled.
    catalog.send_invalid_stock(order_id)
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_ordering_with_invalid_payment(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Test the order creation process with payment failure.

    """
    # Preconditions - OrderingBackground down
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    # Step 1: Create an order and remove items from the basket, ensure entity is created in db.
    basket.send_new_order()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2: Start the ordering background service, ensure status = '2' and verify the items are in stock.
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3: Confirm the order inventory is valid and verify that status is 3.
    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4: Verify that the order status is set to "6"-Cancelled after failed payment.
    payment.send_rejected_payment(order_id)
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))
