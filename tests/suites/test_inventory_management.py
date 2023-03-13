import pytest

from tests.scenarios.scenarios import *


@pytest.mark.inventory_menagement
def test_catalog_stock_validation_process():
    """
    Source Test Case Title: Verify that the order process continues whenever a confirmation message has been sent from the catalog service.

    Source Test Case Purpose: Verify that the integration with the Catalog service and its queue are working.

    Source Test Case ID: 15

    Source Test Case Traceability: 2.3, 4.1
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert catalog_stock_confirmation_scenario()


@pytest.mark.inventory_menagement
def test_catalog_stock_rejection_process():
    """
    Source Test Case Title: Verify that the order is canceled whenever a rejection message has been received from the Catalog service.

    Source Test Case Purpose: Verify that the integration with the Catalog service and its queue are working.

    Source Test Case ID: 22

    Source Test Case Traceability: 4.2
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert Simulator.explicit_status_id_validation(status_id=2, timeout=100)
    # Run step 3
    assert catalog_stock_rejection_scenario()
