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


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_get_orders_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to get all card types is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 28

    Source Test Case Traceability: 5.8
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_ship_order_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to ship order is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 29

    Source Test Case Traceability: 5.9
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_cancel_order_is_denied():
    """
    Source Test Case Title: Verify that an unauthorized request to cancel order is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 30

    Source Test Case Traceability: 5.10
    """
    pass


@pytest.mark.security
@pytest.mark.api
@pytest.mark.scalability
@pytest.mark.reliability
@pytest.mark.loads
def test_order_creation_while_handling_ddos():
    """
    Source Test Case Title: Verify that the service is able to perform 300 orders while DDOS attack is simulated on the service.

    Source Test Case Purpose: Verify that continuously sending an API request to get all the orders will not interrupt the service, while he tries to perform multiple ordering operations.

    Source Test Case ID: 31

    Source Test Case Traceability: 5.11
    """
    pass

