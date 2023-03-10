import json
from time import sleep

import pytest

from simulators.basket_simulator import BasketSimulator
from utils.db.db_utils import MSSQLConnector
from utils.messages.messages_generator import MessageGenerator

pytest.mark.parametrize()


def test_main_success_scenario():
    test_user_can_submit_an_order()
    



def test_user_can_submit_an_order():
    """
    Test to verify order's submission is valid.

        Source Test Case Title: Verify that the user can submit an order.

        Source Test Case Description: Verify that the submitting order functionality of the service is working.

        Source Test Case ID:2

        Source Test Case Traceability: 1.2.1

    """
    basket_mock = BasketSimulator()

    # Message variable is a dictionary with 2 items:
    # 1. An input message to create the order.
    # 2. An output message from the order creation process.
    mg = MessageGenerator()
    messages = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(messages["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    sleep(3)
    expected_message = messages["output"]['UserId']
    actual_message = (json.loads(basket_mock.get_first_message().decode('utf-8')))['UserId']

    assert actual_message == expected_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    with MSSQLConnector() as conn:
        assert len(conn.select_query(
            # In the below query, we fetch the last user order (max order id), and check if it's OrderStatusID is equals to 1.
            "SELECT MAX(o.Id), o.OrderStatusId "
            "FROM ordering.orders o "
            "JOIN ordering.buyers b "
            "ON b.Id = o.BuyerId "
            "WHERE o.OrderStatusId = 1 "
            "GROUP BY o.OrderStatusId"
        )) > 0  # Expected Result #2 - A new order entity has been created within the orders table, with OrderStatusID of 1.


def test_temp():
    b = BasketSimulator()
    b.purge_queue()
