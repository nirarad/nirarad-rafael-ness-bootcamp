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
    Test to verify order's submission is valid.

        Source Test Case Title: Verify that the user can submit an order.

        Source Test Case Description: Verify that the submitting order functionality of the service is working.

        Source Test Case ID:1

        Source Test Case Traceability: 1.1.1
    """
    # Preparing test environment
    basket_mock = BasketSimulator()
    basket_mock.purge_queue()
    sleep(2)
    mg = MessageGenerator()
    basket_to_order_msg = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(basket_to_order_msg["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    sleep(3)
    expected_message = basket_to_order_msg["output"]['UserId']
    actual_message = basket_mock.get_first_message()['UserId']
    assert actual_message == expected_message

    # If we reached here, then the rest of the test will run.
    catalog_to_order_msg = mg.catalog_to_order()
    catalog_simulator = CatalogSimulator()
    catalog_simulator.validate_items_in_stock()
    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert basket_mock.verify_status_id_is_submitted()


def test_user_can_submit_an_order():
    """
    Test to verify order's submission is valid.

        Source Test Case Title: Verify that the user can submit an order.

        Source Test Case Description: Verify that the submitting order functionality of the service is working.

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
