from time import sleep

import pytest
from dotenv import load_dotenv

from simulators.basket_simulator import BasketSimulator
from simulators.catalog_simulator import CatalogSimulator
from utils.messages.messages_generator import MessageGenerator

pytest.mark.parametrize()

load_dotenv()


def test_main_success_scenario():
    """
        Source Test Case Title: Verify the main success scenario for creating order is valid.

        Source Test Case Purpose: Verify that the submitting order functionality of the service is working.

        Source Test Case ID:1

        Source Test Case Traceability: 1.1.1
    """
    # Preparing test environment
    basket_mock = BasketSimulator()
    basket_mock.purge_queue()
    mg = MessageGenerator()
    basket_to_order_msg = mg.basket_to_order()
    sleep(3)

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(basket_to_order_msg["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    expected_message = basket_to_order_msg["output"]['UserId']
    sleep(3)
    actual_message = basket_mock.get_first_message()['UserId']
    assert actual_message == expected_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert basket_mock.verify_status_id_is_submitted()

    # Add additional simulators
    catalog_mock = CatalogSimulator()
    catalog_mock.purge_queue()
    catalog_to_order_msg = mg.catalog_to_order()

    # Step 3 - Verify that the catalog queue received the message from the ordering service.
    catalog_mock.validate_items_in_stock(catalog_to_order_msg["input"])

    # Waiting for the queue to get the massage, and for the status to update for 'awaitingvalidation'.
    sleep(60)

    # Expected Result #3 - The catalog queue received the message from the ordering service.
    expected_message = catalog_to_order_msg["output"]["OrderStatus"]
    actual_message = catalog_mock.get_first_message()["OrderStatus"]
    assert expected_message == actual_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert catalog_mock.verify_state_status_id()


def test_user_can_submit_an_order():
    """
        Source Test Case Title: Verify that the user can submit an order.

        Source Test Case Purpose: Verify that the submitting order functionality of the service is working.

        Source Test Case ID:2

        Source Test Case Traceability: 1.2.1

    """
    # Preparing test environment
    basket_mock = BasketSimulator()
    basket_mock.purge_queue()
    sleep(2)
    mg = MessageGenerator()
    messages = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(messages["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    sleep(3)
    expected_message = messages["output"]['UserId']
    actual_message = basket_mock.get_first_message()['UserId']
    assert actual_message == expected_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert basket_mock.verify_status_id_is_submitted()
