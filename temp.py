from dotenv import load_dotenv

from simulators.basket_simulator import BasketSimulator
from utils.messages.messages_generator import MessageGenerator

load_dotenv()


def temp():
    basket_mock = BasketSimulator()
    mg = MessageGenerator()
    messages = mg.basket_to_order()

    # Step #1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(messages["input"])

    # # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    # sleep(3)
    # expected_message = messages["output"]['UserId']
    # actual_message = basket_mock.get_first_message()['UserId']
    # print(type(actual_message))
    # if actual_message == expected_message:
    #     print("true 1")
    #
    # # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    # if basket_mock.verify_status_id_is_submitted():
    #     print("true 2")


temp()
