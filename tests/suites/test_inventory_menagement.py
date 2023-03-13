import pytest


@pytest.mark.order_tracking
def test_stockconfirmed_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘stockconfirmd’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 15

    Source Test Case Traceability: 2.3, 4.1
    """
    pass


@pytest.mark.inventory_menagement
def test_catalog_rejection_process(purge_all_queues):
    """
    Source Test Case Title: Verify that the order is canceled whenever a rejection message has been received from the Catalog service.

    Source Test Case Purpose: Verify that the integration with the Catalog service and its queue are working.

    Source Test Case ID: 22

    Source Test Case Traceability: 4.2
    """
    pass
