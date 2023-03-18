from time import sleep

from dotenv import load_dotenv

from constants import *
from simulators.basket_simulator import BasketSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.payment_simulator import PaymentSimulator
from simulators.simulator import Simulator
from utils.api.ordering_api import OrderingAPI
from utils.docker.docker_utils import DockerManager
from utils.messages.messages_generator import MessageGenerator

load_dotenv()


def order_submission_scenario():
    """
    Method to simulate the order submission scenario, by sending message to create a new order entity
    from the basket simulator to the ordering queue, and by receiving the output message from the ordering service to the basket queue.
    Returns:
            Returns True only if the basket queue receive and send the correct messages,
            and in the end of the process, the order status id is 1 (submitted).
    Raises:
        AssertionError: Raised if the basket queue has not received or sent the correct messages, or in a case that in the end of the process, the order status id is not 1 (submitted).
    """
    # Preparing test environment
    basket_mock = BasketSimulator()
    mg = MessageGenerator()
    basket_to_ordering_msg = mg.basket_to_ordering()

    # Step 1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.send_message_to_create_an_order(basket_to_ordering_msg["input"])

    # Expected Result #1 - The basket queue received the correct output message (from the Message dictionary).
    actual_message = basket_mock.get_first_message()
    expected_message = basket_to_ordering_msg["output"]

    retry_attempts = 1
    retry_max = 2

    # If the message does not reach the queue, retry the test.
    if actual_message is None and retry_attempts <= retry_max:
        print(
            f"There with the basket queue connection. Restarting the Basket service at {retry_attempts} retry attempt.")

        # Restart the simulator related container.
        docker_manager = DockerManager()
        docker_manager.restart(BASKET_SERVICE)
        sleep(4)

        # Retry the process.
        basket_mock.send_message_to_create_an_order(basket_to_ordering_msg["input"])
        actual_message = basket_mock.get_first_message()
        expected_message = basket_to_ordering_msg["output"]

        retry_attempts -= 1

    # Verify that the correct message has been sent from the ordering service to the basket queue.
    if actual_message['UserId'] != expected_message['UserId']:
        raise AssertionError(f"Test failed. Failure reason is: {actual_message} != {expected_message}.")

    # Step 2 - Verify that a new order entity has been created within the orders table, with OrderStatusID of 1.
    if not basket_mock.verify_status_id_is_submitted():
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'submitted' status (status number 1).")

    # Test Passed
    return True


def order_submission_without_response_waiting_scenario():
    """
    Function to simulate the order submission scenario, by sending a message to create a new order entity
    from the basket simulator to the ordering queue.
    This function do not verify a valid response from the ordering service.
    """
    # Preparing test environment
    basket_mock = BasketSimulator()
    mg = MessageGenerator()
    basket_to_ordering_msg = mg.basket_to_ordering()

    # step 1 - Send from the basket mock to the Ordering queue massage to create a new order.
    basket_mock.send_message_to_create_an_order(basket_to_ordering_msg["input"])


def catalog_stock_confirmation_scenario():
    """
    Function to simulate the catalog stock confirmation scenario, by sending message to validate that the order items in stock.
    Returns:
            Returns True only if before sending the message the order status is awaitingvalidation (2),
            and in the end of the process, the order status id is 3 (stockconfirmed).
    Raises:
        AssertionError: Raised if before sending the message the order status is not awaitingvalidation (2), or in case that in the end of the process, the order status is not 3 (stockconfirmed).
    """
    # Preparing test environment
    catalog_mock = CatalogSimulator()
    mg = MessageGenerator()
    catalog_to_ordering_msg = mg.catalog_to_ordering(catalog_mock.CURRENT_ORDER_ID)

    # Step/Expected Result 1 - The catalog queue received the message from the ordering service, so the OrderStatusID in the orders table is updated to 2
    # The maximum time to wait for the order status to be updated is 30 seconds
    if not catalog_mock.verify_status_id_is_awaiting_validation(timeout=300):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'awaitingvalidation' status (status number 2).")

    # step 2 - Send from the catalog mock to the Ordering queue the massage to change status to 'stockconfirmed'.
    catalog_mock.send_message_to_validate_items_in_stock(catalog_to_ordering_msg["input"])

    # Expected Result #3 - The OrderStatusID in the orders table has been updated to 3.
    if not catalog_mock.verify_status_id_is_stock_confirmed(timeout=300):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'stockconfirmed' status (status number 3).")

    # Test Passed
    return True


def catalog_stock_confirmation_without_waiting_for_response_scenario():
    """
    Function to simulate the catalog stock confirmation scenario, by sending message to validate that the order items in stock.
    Returns:
            Returns True only if the order status is awaitingvalidation (2).
    Raises:
        AssertionError: Raised if before sending the message the order status is not awaitingvalidation (2).
    """
    # Preparing test environment
    catalog_mock = CatalogSimulator()
    mg = MessageGenerator()
    catalog_to_ordering_msg = mg.catalog_to_ordering(catalog_mock.CURRENT_ORDER_ID)

    # Step/Expected Result 1 - The catalog queue received the message from the ordering service, so the OrderStatusID in the orders table is updated to 2
    # The maximum time to wait for the order status to be updated is 30 seconds
    if not catalog_mock.verify_status_id_is_awaiting_validation(timeout=300):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'awaitingvalidation' status (status number 2).")

    # step 2 - Send from the catalog mock to the Ordering queue the massage to change status to 'stockconfirmed'.
    catalog_mock.send_message_to_validate_items_in_stock(catalog_to_ordering_msg["input"])

    # Test Passed
    return True


def catalog_stock_rejection_scenario():
    """
    Function to simulate the catalog stock rejection scenario, by sending message to inform that one or more order items out of stock.
    Returns:
            Returns True only if before sending the message the order status is awaitingvalidation (2),
            and in the end of the process, the order status id is 6 (canceled).
    Raises:
        AssertionError: Raised if before sending the message the order status is not awaitingvalidation (2), or in case that in the end of the process, the order status is not 6 (canceled).
    """
    # Preparing test environment
    catalog_mock = CatalogSimulator()
    mg = MessageGenerator()
    catalog_to_ordering_invalid_msg = mg.catalog_rejection_to_ordering(catalog_mock.CURRENT_ORDER_ID)

    # Step/Expected Result 1 - The catalog queue received the message from the ordering service, so the OrderStatusID in the orders table is updated to 2
    # The maximum time to wait for the order status to be updated is 30 seconds
    if not catalog_mock.verify_status_id_is_awaiting_validation(timeout=300):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'awaitingvalidation' status (status number 2).")

    # step 2 - Send from the catalog mock to the Ordering queue the massage to change status to 'stockconfirmed'.
    catalog_mock.send_message_to_inform_items_not_in_stock(catalog_to_ordering_invalid_msg)

    # Expected Result #2 - The OrderStatusID is updated to 6.
    if not Simulator.explicit_status_id_validation(CANCELED_STATUS):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'canceled' status (status number 6).")

    # Test Passed
    return True


def payment_confirmation_scenario():
    """
    Function to simulate the payment process confirmation scenario, by sending message to validate that the payment process succeeded.
    Returns:
            Returns True only if the payment queue received and send the correct messages,
            and in the end of the process, the order status id is 4 (paid).
    Raises:
        AssertionError: Raised if the payment queue has not received or sent the correct messages, or in a case that in the end of the process, the order status id is not 4 (paid).
    """
    # Preparing test environment
    payment_mock = PaymentSimulator()
    messages = MessageGenerator()
    payment_to_ordering_msg = messages.payment_to_ordering(payment_mock.CURRENT_ORDER_ID)

    # step 1 - Verify that the payment queue received from the correct message from the ordering service.
    expected_result = [payment_to_ordering_msg["output"]["OrderId"], payment_to_ordering_msg["output"]["OrderStatus"]]
    message_from_queue = payment_mock.get_first_message()
    actual_result = [message_from_queue["OrderId"], message_from_queue["OrderStatus"]]

    # Expected Result #1 - The payment queue received the correct message from the ordering service.
    if actual_result[0] != expected_result[0] or actual_result[1] != expected_result[1]:
        raise AssertionError(
            f"Test failed. Failure reason is: {actual_result[0]} != {expected_result[0]} or {actual_result[1]} != {expected_result[1]} ")

    # step 2 - Send from the payment mock to the Ordering message that confirms the payment process.
    payment_mock.send_message_to_validate_payment(payment_to_ordering_msg["input"])

    # Expected Result #2 - The OrderStatusID is updated to 4.
    if not payment_mock.verify_status_id_is_paid(400):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'paid' status (status number 4).")

    # Test Passed
    return True


def payment_rejection_scenario():
    """
     Function to simulate the payment process rejection scenario, by sending message to inform that the payment process has failed.
     Returns:
             Returns True only if before sending the message the order status is canceled (6).
     Raises:
         AssertionError: Raised in case that in the end of the process, the order status is not 6 (canceled).
     """
    # Preparing test environment
    payment_mock = PaymentSimulator()
    messages = MessageGenerator()
    payment_to_ordering_invalid_msg = messages.payment_rejection_to_order(payment_mock.CURRENT_ORDER_ID)

    # step 1 - Send from the payment mock to the Ordering message that rejects the payment process.
    payment_mock.inform_payment_process_failed(payment_to_ordering_invalid_msg)

    # Expected Result #2 - The OrderStatusID is updated to 6.
    if not Simulator.explicit_status_id_validation(CANCELED_STATUS):
        raise AssertionError(
            f"Test failed. Failure reason is: The order status hasn't been changed to the 'canceled' status (status number 6).")

    # Test Passed
    return True


def ship_api_request_scenario(status_code=200, id_validation_timeout=300):
    """
    Function to simulate an 'order shipping' request that have been sent to the  Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
        id_validation_timeout: The max number of seconds to validate the id.
    Returns:
        True only if the returned status code is equal to 200 and the id in the end of the process is 5.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned, or the order status is not 5.
    """
    # step 1 - Send the following API request to ship the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if ordering_api.ship_order(Simulator.CURRENT_ORDER_ID).status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # The OrderStatusID in the orders table updated to 5.
    if status_code == 200:
        if not Simulator.explicit_status_id_validation(SHIPPED_STATUS, timeout=id_validation_timeout):
            raise AssertionError(
                f"Test failed. Failure reason is: The order status hasn't been changed to the 'shipped' status (status number 5).")

    # Test Passed
    return True


def ship_invalid_auth_api_request_scenario(status_code=401):
    """
    Function to simulate a scenario of an unauthorized 'order shipping' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 401.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """
    # step 1 - Send the following API request to ship the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 401 HTTP status code should be returned.
    if ordering_api.ship_order_invalid_auth(Simulator.CURRENT_ORDER_ID).status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def cancel_api_request_scenario(status_code=200, timeout=200):
    """
    Function to simulate a scenario of an 'order canceling' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
        timeout: The max number of seconds to validate the id.
    Returns:
        True only if the returned status code is equal to 200 and the id in the end of the process is 6
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned, or the order status is not 6.
    """
    # step 1 - Send the following API request to cancel the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if not ordering_api.cancel_order(Simulator.CURRENT_ORDER_ID).status_code == status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # In case that the status code is 200, OrderStatusID in the orders table should be updated to 6.
    if status_code == 200:
        if not Simulator.explicit_status_id_validation(CANCELED_STATUS, timeout=timeout):
            raise AssertionError(
                f"Test failed. Failure reason is: The order status hasn't been changed to the  'cancel' status (status number 6).")

    # Test Passed
    return True


def cancel_invalid_auth_api_request_scenario(status_code=401):
    """
    Function to simulate a scenario of an unauthorized 'order canceling' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 401.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to cancel the order.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 401 HTTP status code should be returned.
    if ordering_api.cancel_order_invalid_auth(Simulator.CURRENT_ORDER_ID).status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_orders_api_request_scenario(status_code=200):
    """
    Function to simulate a scenario of a 'get all orders' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 200.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get all the orders of the user.
    ordering_api = OrderingAPI()
    response = ordering_api.get_orders()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if response.status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_orders_invalid_auth_api_request_scenario(status_code=401):
    """
    Function to simulate a scenario of an unauthorized request to 'get all orders' that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 401.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get all the orders of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 401 status code should be returned.
    if ordering_api.get_orders_invalid_auth().status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_order_by_id_api_request_scenario(status_code=200):
    """
    Function to simulate a scenario of a 'get order by id' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 200.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get one of the user orders by its id.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if ordering_api.get_order_by_id(Simulator.CURRENT_ORDER_ID).status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_order_by_id_invalid_auth_api_request_scenario(status_code=401):
    """
    Function to simulate a scenario of an unauthorized 'get order by id' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 401.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get one of the user orders by its id.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if ordering_api.get_orders_invalid_auth().status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_card_types_api_request_scenario(status_code=200):
    """
    Function to simulate a scenario of a 'get card types' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 200.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get all the card types of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if ordering_api.get_card_types().status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def get_card_types_invalid_auth_api_request_scenario(status_code=401):
    """
    Function to simulate a scenario of an unauthorized 'get order card types' request that have been sent to the Ordering API.
    Parameters:
        status_code: The expected status code to be returned.
    Returns:
        True only if the returned status code is equal to 401.
     Raises:
         AssertionError: Raised in case that The expected status code hasn't been returned.
    """

    # step 1 - Send the following API request to get all the card types of the user.
    ordering_api = OrderingAPI()

    # Expected Result #1 - 200 HTTP status code should be returned.
    if ordering_api.get_card_types_invalid_auth().status_code != status_code:
        raise AssertionError(
            f"Test failed. Failure reason is: Status Code {status_code} hasn't been returned.")

    # Test Passed
    return True


def crash_ordering_service_scenario(docker_manager):
    """
    Function to simulate a service crash scenario.
    Parameters:
        docker_manager: The docker manager to use.
    """
    # Stop all the mentioned services.
    docker_manager.stop(ORDERING_SERVICE)
    docker_manager.stop(ORDERING_BACKGROUND_TASK_SERVICE)
    docker_manager.stop(ORDERING_SERVICE)
    docker_manager.stop(SIGNALR_HUB_SERVICE)
    docker_manager.stop(ORDERING_SERVICE)
