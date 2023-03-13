import pytest
from dotenv import load_dotenv

from simulators.basket_simulator import BasketSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.payment_simulator import PaymentSimulator
from simulators.simulator import Simulator
from utils.api.ordering_api import OrderingAPI
from utils.messages.messages_generator import MessageGenerator

load_dotenv()


# pytestmark = pytest.mark.skip(reason="Scenario function which meant to serve other tests.")


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_order_submission_scenario():
    # Preparing test environment
    basket_mock = BasketSimulator()
    mg = MessageGenerator()
    basket_to_ordering_msg = mg.basket_to_order()

    # step 1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.create_order(basket_to_ordering_msg["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    actual_message = basket_mock.get_first_message()['UserId']
    expected_message = basket_to_ordering_msg["output"]['UserId']
    assert actual_message == expected_message

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    assert basket_mock.verify_status_id_is_submitted()


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_catalog_stock_confirmation_scenario():
    # Preparing test environment
    catalog_mock = CatalogSimulator()
    mg = MessageGenerator()
    catalog_to_ordering_msg = mg.catalog_to_order(catalog_mock.CURRENT_ORDER_ID)

    # Step/Expected Result 1 - The catalog queue received the message from the ordering service, so the OrderStatusID in the orders table is updated to 2
    # The maximum time to wait for the order status to be updated is 30 seconds
    assert catalog_mock.verify_status_id_is_awaiting_validation(timeout=300)

    # step 2 - Send from the catalog mock to the Ordering queue the massage to change status to 'stockconfirmed'.
    catalog_mock.validate_items_in_stock(catalog_to_ordering_msg["input"])

    # Expected Result #3 - The OrderStatusID in the orders table has been updated to 3.
    assert catalog_mock.verify_status_id_is_stock_confirmed(timeout=300)


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_payment_confirmation_scenario():
    # Preparing test environment
    payment_mock = PaymentSimulator()
    messages = MessageGenerator()
    payment_to_ordering_msg = messages.payment_to_order(payment_mock.CURRENT_ORDER_ID)

    # step 1 - Verify that the payment queue received from the correct message from the ordering service.
    expected_result = [payment_to_ordering_msg["output"]["OrderId"], payment_to_ordering_msg["output"]["OrderStatus"]]
    message_from_queue = payment_mock.get_first_message()
    actual_result = [message_from_queue["OrderId"], message_from_queue["OrderStatus"]]

    # Expected Result #1 - The payment queue received the correct message from the ordering service.
    assert actual_result[0] == expected_result[0] and actual_result[1] == expected_result[1]

    # step 2 - Send from the payment mock to the Ordering message that confirms the payment process.
    payment_mock.validate_payment(payment_to_ordering_msg["input"])

    # Expected Result #2 - The OrderStatusID is updated to 4.
    assert payment_mock.verify_status_id_is_paid(400)


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_ship_api_request_scenario(status_code=200, id_validation_timeout=300):
    # step 1 - Send the following API request to ship the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.ship_order(Simulator.CURRENT_ORDER_ID).status_code == status_code

    # The OrderStatusID in the orders table updated to 5.
    if status_code == 200:
        assert Simulator.explicit_status_id_validation(5, timeout=id_validation_timeout)


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_ship_invalid_auth_api_request_scenario(status_code=401):
    # step 1 - Send the following API request to ship the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.ship_order_invalid_auth(Simulator.CURRENT_ORDER_ID).status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_cancel_api_request_scenario(status_code=200, timeout=200):
    # step 1 - Send the following API request to cancel the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.cancel_order(Simulator.CURRENT_ORDER_ID).status_code == status_code

    # In case that the status code is 200, OrderStatusID in the orders table should be updated to 6.
    if status_code == 200:
        assert Simulator.explicit_status_id_validation(6, timeout=timeout)


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_cancel_invalid_auth_api_request_scenario(status_code=401):
    # step 1 - Send the following API request to cancel the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.cancel_order_invalid_auth(Simulator.CURRENT_ORDER_ID).status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_orders_api_request_scenario(status_code=200):
    # step 1 - Send the following API request to get all the orders of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_orders().status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_orders_invalid_auth_api_request_scenario(status_code=401):
    # step 1 - Send the following API request to get all the orders of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_orders_invalid_auth().status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_order_by_id_api_request_scenario(status_code=200):
    # step 1 - Send the following API request to get one of the user orders by its id.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_order_by_id(Simulator.CURRENT_ORDER_ID).status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_order_by_id_invalid_auth_api_request_scenario(status_code=401):
    # step 1 - Send the following API request to get one of the user orders by its id.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_orders_invalid_auth().status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_card_types_api_request_scenario(status_code=200):
    # step 1 - Send the following API request to get all the card types of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_card_types().status_code == status_code


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
def test_get_card_types_invalid_auth_api_request_scenario(status_code=401):
    # step 1 - Send the following API request to get all the card types of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    assert ordering_api.get_card_types_invalid_auth().status_code == status_code


# Exclude the skip variable from the module, so we can import the all module
__all__ = [name for name in dir() if not name.startswith('_') and name != 'pytestmark']
