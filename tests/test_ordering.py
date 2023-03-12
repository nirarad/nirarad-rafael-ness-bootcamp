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
@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
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


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
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


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
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


@pytest.mark.skip(reason="Scenario function which meant to serve other tests")
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


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_1():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘submitted’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 1.

    Source Test Case ID: 3

    Source Test Case Traceability: 1.3.1, 5.4
    """
    pass


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_2():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘awaitingvalidation’..

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 2.

    Source Test Case ID: 4

    Source Test Case Traceability: 1.3.2, 5.4
    """
    pass


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_3():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘stockconfirmd’.

    Source Test Case Purpose:  Verify that the canceling order functionality of the microservice is working on order status number 3.

    Source Test Case ID: 5

    Source Test Case Traceability: 1.3.3, 5.4
    """
    pass


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_not_cancel_order_on_status_4():
    """
    Source Test Case Title:Verify that the user can not cancel his order when the order status is ‘paid’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 4.

    Source Test Case ID: 6

    Source Test Case Traceability: 1.3.4
    """
    pass


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_not_cancel_order_on_status_5():
    """
    Source Test Case Title: Verify that the user can not cancel his order when the order status is ‘paid’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 5.

    Source Test Case ID: 7

    Source Test Case Traceability: 1.3.5
    """
    pass


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_ship_order_on_status_4():
    """
    Source Test Case Title: Verify that the service allows updating order status to ‘shipped’ from ‘paid’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (updating the status) on order status number 4.

    Source Test Case ID: 8

    Source Test Case Traceability: 1.4.1,5.5
    """
    pass


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_1():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to ‘shipped’ from ‘submitted’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status)  on order status number 1.

    Source Test Case ID: 9

    Source Test Case Traceability: 1.4.2
    """
    pass


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_2():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to ‘shipped’ from ‘awatingvalidation’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 2.

    Source Test Case ID: 10

    Source Test Case Traceability: 1.4.3
    """
    pass


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_3():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to  ‘shipped’  from ‘stockconfirmd’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 3.

    Source Test Case ID: 11

    Source Test Case Traceability: 1.4.4
    """
    pass


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_6():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to  ‘shipped’ from ‘canceled’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 6.

    Source Test Case ID: 12

    Source Test Case Traceability: 1.4.5
    """
    pass


@pytest.mark.order_tracking
def test_submitted_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘submitted’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 13

    Source Test Case Traceability: 2.1
      """
    pass


@pytest.mark.order_tracking
def test_awatingvalidation_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘awatingvalidation’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 14

    Source Test Case Traceability: 2.2
      """
    pass


@pytest.mark.order_tracking
def test_stockconfirmed_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘stockconfirmd’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 15

    Source Test Case Traceability: 2.3, 4.1
    """
    pass


@pytest.mark.order_tracking
def test_paid_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘paid’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 16

    Source Test Case Traceability: 2.4
    """
    pass


@pytest.mark.order_tracking
def test_shipped_order_status_appears_on_correct_state():
    """
     Source Test Case Title: Verify that the ‘shipped’ order status appears at the correct service state.

     Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

     Source Test Case ID: 17

     Source Test Case Traceability: 2.5
     """
    pass


@pytest.mark.order_tracking
def test_canceled_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘canceled’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 18

    Source Test Case Traceability: 2.6
     """
    pass


@pytest.mark.payment_processing
def test_payment_validation_process():
    """
    Source Test Case Title: Verify that the order process continues whenever the payment process has succeeded

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 19

    Source Test Case Traceability: 3.1
     """
    pass


@pytest.mark.payment_processing
def test_payment_rejection_process():
    """
    Source Test Case Title: Verify that the order is canceled whenever the payment process has failed.

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 20

    Source Test Case Traceability: 3.2
     """
    pass


@pytest.mark.payment_processing
@pytest.mark.canceling_order
def test_payment_process_rejection_caused_by_server_timeout():
    """
    Source Test Case Title: Validate that the service will cancel the ordering process when the service is on ‘confirmstock’ status and the user does not initiate any action for 1 hour.

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 21

    Source Test Case Traceability: 3.3
    """
    pass

@pytest.mark.ordering_management
def test_catalog_rejection_process():
    """
    Source Test Case Title: Verify that the order is canceled whenever a rejection message has been received from the Catalog service.

    Source Test Case Purpose: Verify that the integration with the Catalog service and its queue are working.

    Source Test Case ID: 22

    Source Test Case Traceability: 4.2
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_orders_access():
    """
    Source Test Case Title: Verify that a signed-in user is only exposed to his own orders.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users orders.

    Source Test Case ID: 23

    Source Test Case Traceability: 5.1
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_order_by_id_access():
    """
    Source Test Case Title: Verify that a signed-in user is only exposed to his own card types.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users card types.

    Source Test Case ID: 24

    Source Test Case Traceability: 5.2
    """
    pass


@pytest.mark.security
@pytest.mark.api
@pytest.mark.canceling_order
def test_authorized_user_order_canceling():
    """
    Source Test Case Title: Verify that a signed-in user receives only his own orders when he tries to fetch an order by id.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users card types.

    Source Test Case ID: 25

    Source Test Case Traceability: 5.3
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_orders_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to get all orders is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 26

    Source Test Case Traceability: 5.6
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_order_by_id_is_denied():
    """
    Source Test Case Title: VVerify that an unauthorized request to get an order by id is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 27

    Source Test Case Traceability: 5.7
    """
    pass
