import pytest


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_orders_access(purge_all_queues):
    """
    Source Test Case Title: Verify that a signed-in user is only exposed to his own orders.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users orders.

    Source Test Case ID: 23

    Source Test Case Traceability: 5.1
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_authorized_user_order_by_id_access(purge_all_queues):
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
def test_authorized_user_order_canceling(purge_all_queues):
    """
    Source Test Case Title: Verify that a signed-in user receives only his own orders when he tries to fetch an order by id.

    Source Test Case Purpose: Verify that the user cannot be exposed to other users card types.

    Source Test Case ID: 25

    Source Test Case Traceability: 5.3
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_orders_is_denied(purge_all_queues):
    """
    Source Test Case Title: Verify that an unauthorized request to get all orders is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 26

    Source Test Case Traceability: 5.6
    """
    pass


@pytest.mark.security
@pytest.mark.api
def test_unauthorized_request_for_order_by_id_is_denied(purge_all_queues):
    """
    Source Test Case Title: VVerify that an unauthorized request to get an order by id is denied.

    Source Test Case Purpose: Verify that the microservice API is designed to deny unauthorized requests.

    Source Test Case ID: 27

    Source Test Case Traceability: 5.7
    """
    pass
