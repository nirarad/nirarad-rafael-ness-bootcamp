import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.Api.ordering_api import OrderingAPI
from Tests.test_ordering_service import test_mss
from Utils.DB.db_functions import *


######################################################################################################################################################################################
##################################### --------------------------Functional Tests-----------------------###############################################################################
######################################################################################################################################################################################

def test_get_all_orders(ordering_api: OrderingAPI):
    """
    Test the retrieval of all orders.
    This test verifies that the orders retrieval endpoint returns a HTTP 200 status code.

    """
    reponse_body, status_code = ordering_api.get_all_orders()
    assert status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert len(reponse_body) == len(select_orders_by_buyer_id(1))


def test_get_order_by_id(ordering_api: OrderingAPI):
    """
    Test the retrieval of an order by its ID.
    This test verifies that the order retrieval endpoint returns a HTTP 200 status code.

    """
    assert ordering_api.get_order_by_id(3).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))


def test_negative_get_order_by_id(ordering_api: OrderingAPI):
    assert ordering_api.get_order_by_id(0).status_code == int(
        os.getenv('NOT_FOUND_RESPOSE_CODE'))


def test_get_cardtypes(ordering_api: OrderingAPI):
    assert ordering_api.get_cardtypes().status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))


def test_cancel_submitted_order(ordering_api: OrderingAPI, basket: BasketMock):
    """
    Test the cancellation of an order with "submitted" status.

    """
    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_cancel_awaitingvalidation_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    """
    Test the cancellation of an order with "awaiting validation" status.

    """
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_cancel_stockconfirmed_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    """
    Test the cancellation of an order with "stock confirmed" status.

    """
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_negative_cancel_order_after_payment(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Negative Test the cancellation of an order with either 'Paid' or 'Shipped' or 'Cancel' Status.

    """
    test_mss(docker_manager, basket, catalog, payment)
    order_id = select_last_order()['Id']

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

    ordering_api.ship_order(order_id)
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


def test_ship_paid_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    """
    Test shipping an order with "Paid" status.

    """
    test_mss(docker_manager, basket, catalog, payment)
    order_id = select_last_order()['Id']

    assert ordering_api.ship_order(order_id).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


def test_negative_ship_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    """
    Negative test shipping an order with status 1 - 3, and 6.

    """
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(
        os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(
        os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))
