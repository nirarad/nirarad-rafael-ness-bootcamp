from time import sleep

import pytest
from dotenv import load_dotenv

from simulators.basket_simulator import BasketSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.payment_simulator import PaymentSimulator
from simulators.simulator import Simulator
from utils.api.ordering_api import OrderingAPI
from utils.messages.messages_generator import MessageGenerator

load_dotenv()


# region Scenarios tests
@pytest.mark.skip(reason="Scenario function which meant to service other tests")
def test_order_submission():
    # Preparing test environment
    basket_mock = BasketSimulator()
    sleep(2)
    mg = MessageGenerator()
    basket_to_ordering_msg = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(basket_to_ordering_msg["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    expected_message = basket_to_ordering_msg["output"]['UserId']
    actual_message = (basket_mock.get_first_message())['UserId']
    assert actual_message == expected_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert basket_mock.verify_status_id_is_submitted()


@pytest.mark.skip(reason="Scenario function which meant to service other tests")
def test_catalog_stock_confirmation():
    # Preparing test environment
    catalog_mock = CatalogSimulator()
    mg = MessageGenerator()
    catalog_to_ordering_msg = mg.catalog_to_order(catalog_mock.CURRENT_ORDER_ID)

    # Step/Expected Result 1 - The catalog queue received the message from the ordering service, so the OrderStatusID in the orders table is updated to 2
    # The maximum time to wait for the order status to be updated is 30 seconds
    assert catalog_mock.verify_status_id_is_awaiting_validation(timeout=300)

    # Step #2 - Send from the catalog mock to the Ordering queue the massage to change status to 'stockconfirmed'.
    catalog_mock.validate_items_in_stock(catalog_to_ordering_msg["input"])

    # Expected Result #3 - The OrderStatusID in the orders table has been updated to 3.
    assert catalog_mock.verify_status_id_is_stock_confirmed(timeout=300)


@pytest.mark.skip(reason="Scenario function which meant to service other tests")
def test_payment_confirmation():
    # Preparing test environment
    payment_mock = PaymentSimulator()
    messages = MessageGenerator()
    payment_to_ordering_msg = messages.payment_to_order(payment_mock.CURRENT_ORDER_ID)

    # Step #1 - Verify that the payment queue received from the correct message from the ordering service.
    expected_result = [payment_to_ordering_msg["output"]["OrderId"], payment_to_ordering_msg["output"]["OrderStatus"]]
    message_from_queue = payment_mock.get_first_message()
    actual_result = [message_from_queue["OrderId"], message_from_queue["OrderStatus"]]

    # Expected Result #1 - The payment queue received the correct message from the ordering service.
    assert actual_result[0] == expected_result[0] and actual_result[1] == expected_result[1]

    # Step #2 - Send from the payment mock to the Ordering message that confirms the payment process.
    payment_mock.validate_payment(payment_to_ordering_msg["input"])

    # Expected Result #2 - The OrderStatusID is updated to 4.
    assert payment_mock.verify_status_id_is_paid(400)


@pytest.mark.skip(reason="Scenario function which meant to service other tests")
def test_ship_api_request():
    # Step #1 - Send the following ship API request from Postman.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.ship_order(Simulator.CURRENT_ORDER_ID).status_code == 200
    
    # The OrderStatusID in the orders table updated to 5.
    assert Simulator.implicit_status_id_validation(5)


# endregion
@pytest.mark.order_management
@pytest.mark.main_sucsess_scenario
def test_main_success_scenario():
    """
        Source Test Case Title: Verify the main success scenario for creating order is valid.
        Source Test Case Purpose: Verify that the submitting order functionality of the service is working.
        Source Test Case ID:1
        Source Test Case Traceability: 1.1.1
    """
    # Purge all queues before start
    Simulator.purge_all_queues(
        ['Ordering', 'Basket', 'Catalog', 'Payment', 'Ordering.signalrhub', 'Webhooks', 'BackgroundTasks'])
    # Run steps 1-2
    test_order_submission()
    # Run steps 3-5
    test_catalog_stock_confirmation()
    # Run steps 5-6
    test_payment_confirmation()
    # Run step 7
    test_ship_api_request()


@pytest.mark.order_management
@pytest.mark.creating_order
def test_user_can_submit_an_order():
    """
        Source Test Case Title: Verify that the user can submit an order.
        Source Test Case Purpose: Verify that the submitting order functionality of the service is working.
        Source Test Case ID: 2
        Source Test Case Traceability: 1.2.1
    """
    test_order_submission()
