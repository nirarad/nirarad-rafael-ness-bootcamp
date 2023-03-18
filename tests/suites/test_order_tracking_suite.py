import pytest

from constants import *
from tests.scenarios.scenarios import *


@pytest.mark.order_tracking
def test_submitted_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘submitted’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 13

    Source Test Case Traceability: 2.1
    """
    # Run step 1-2
    assert order_submission_scenario()


@pytest.mark.order_tracking
def test_awatingvalidation_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘awatingvalidation’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 14

    Source Test Case Traceability: 2.2
      """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert EShopSystem.explicit_status_id_validation(status_id=AWAITING_VALIDATION_STATUS, timeout=100)


@pytest.mark.order_tracking
def test_stockconfirmed_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘stockconfirmd’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 15

    Source Test Case Traceability: 2.3, 4.1
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert catalog_stock_confirmation_scenario()


@pytest.mark.order_tracking
def test_paid_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘paid’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 16

    Source Test Case Traceability: 2.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run Steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run Steps 4-5
    assert payment_confirmation_scenario()


@pytest.mark.order_tracking
def test_shipped_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘shipped’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 17

    Source Test Case Traceability: 2.5
    """
    # Run step 1
    assert order_submission_scenario()
    # Run steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run steps 4-5
    assert payment_confirmation_scenario()
    # Run step 6-7
    assert ship_api_request_scenario()


@pytest.mark.order_tracking
def test_canceled_order_status_appears_on_correct_state():
    """
    Source Test Case Title: Verify that the ‘canceled’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 18

    Source Test Case Traceability: 2.6
    """
    # Run step 1
    assert order_submission_scenario()
    # Run steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run steps 4-5
    assert cancel_api_request_scenario()
