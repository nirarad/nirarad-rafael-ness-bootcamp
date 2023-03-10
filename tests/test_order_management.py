import json

import pytest

from simulators.basket_simulator import BasketSimulator
from utils.messages.messages_generator import MessageGenerator

pytest.mark.parametrize()


def test_user_can_submit_an_order():
    basket_mock = BasketSimulator()

    # Message variable is a dictionary with 2 items:
    # 1. An input message to create the order.
    # 2. An output message from the order creation process.
    mg = MessageGenerator()
    messages = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(messages["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    expected_message = messages["output"]['UserId']
    actual_message = (json.loads(basket_mock.get_first_message().decode('utf-8')))['UserId']

    assert actual_message == expected_message

    def test_misc():
        pass
