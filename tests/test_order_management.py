import pytest

from simulators.basket_simulator import BasketSimulator
from utils.messages.messages_generator import MessageGenerator

pytest.mark.parametrize()


def test_user_can_submit_an_order():
    mg = MessageGenerator()
    basket = BasketSimulator()
    messages = mg.basket_to_order()
    basket.create_order(messages["input"])
    # assert basket.get_first_message() == messages["output"]
