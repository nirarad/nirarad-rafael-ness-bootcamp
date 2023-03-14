import pytest

from tests.scenarios.scenarios import *


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_orders_access():
    """
    Source Test Case Title: Verify that a signed-in user is only exposed to his own orders.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users orders.

    Source Test Case ID: 23

    Source Test Case Traceability: 5.1
    """
    # Run step 1
    assert get_orders_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_card_types_access():
    """
    Source Test Case Title: Verify that a signed-in user is only exposed to his own card types.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users card types.

    Source Test Case ID: 24

    Source Test Case Traceability: 5.2
    """
    # Run step 1
    assert get_card_types_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_card_types_access():
    """
    Source Test Case Title: Verify that a signed-in user receives only his own orders when he tries to fetch an order by id.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users orders (by order number).

    Source Test Case ID: 25

    Source Test Case Traceability: 5.3
    """
    # Run step 1
    assert get_card_types_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_orders_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to get all orders is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 26

    Source Test Case Traceability: 5.6
    """
    assert get_orders_invalid_auth_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_order_by_id_is_denied():
    """
    Source Test Case Title: VVerify that an unauthorized request to get an order by id is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 27

    Source Test Case Traceability: 5.7
    """
    assert get_order_by_id_invalid_auth_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_get_card_types_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to get all card types is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 28

    Source Test Case Traceability: 5.8
    """
    assert get_card_types_invalid_auth_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_ship_order_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to ship order is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 29

    Source Test Case Traceability: 5.9
    """
    assert ship_invalid_auth_api_request_scenario()


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_cancel_order_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to cancel order is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 30

    Source Test Case Traceability: 5.10
    """
    assert cancel_invalid_auth_api_request_scenario()


@pytest.mark.skip(reason="Designated for nightly execution.")
@pytest.mark.security
@pytest.mark.api
@pytest.mark.scalability
@pytest.mark.reliability
@pytest.mark.loads
@pytest.mark.nightly
def test_order_creation_while_handling_ddos_simulation(ddos_simulation):
    """
    Source Test Case Title: Verify that the service is able to perform 300 orders while DDOS attack is simulated on the service.

    Source Test Case Purpose: Verify that continuously sending an API request to get all the orders will not interrupt the service, while he tries to perform multiple ordering operations.

    Source Test Case ID: 31

    Source Test Case Traceability: 5.11
    """
    create_order_thread, get_orders_thread, stop_event = ddos_simulation

    # Save the last order id before the ddos_simulation start.
    start_order_id = Simulator.get_max_order_id()

    # Start the order creation thread.
    create_order_thread.start()

    # Start the get orders request thread.
    get_orders_thread.start()

    # Wait for the 2 threads to finish.
    create_order_thread.join()
    get_orders_thread.join()

    end_order_id = Simulator.CURRENT_ORDER_ID

    # Assert that the new orders thread reached the new order's goal number.
    assert create_order_thread.goal == 2

    # Assert that the excepted number of orders entered to the orders table.
    assert 1 + end_order_id - start_order_id == 2
