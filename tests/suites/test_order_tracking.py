from tests.scenarios.test_scenarions import *


@pytest.mark.order_tracking
def test_submitted_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘submitted’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 13

    Source Test Case Traceability: 2.1
      """
    pass


@pytest.mark.order_tracking
def test_awatingvalidation_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘awatingvalidation’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 14

    Source Test Case Traceability: 2.2
      """
    pass


@pytest.mark.order_tracking
def test_stockconfirmed_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘stockconfirmd’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 15

    Source Test Case Traceability: 2.3, 4.1
    """
    pass


@pytest.mark.order_tracking
def test_paid_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘paid’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 16

    Source Test Case Traceability: 2.4
    """
    pass


@pytest.mark.order_tracking
def test_shipped_order_status_appears_on_correct_state(purge_all_queues):
    """
     Source Test Case Title: Verify that the ‘shipped’ order status appears at the correct service state.

     Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

     Source Test Case ID: 17

     Source Test Case Traceability: 2.5
     """
    pass


@pytest.mark.order_tracking
def test_canceled_order_status_appears_on_correct_state(purge_all_queues):
    """
    Source Test Case Title: Verify that the ‘canceled’ order status appears at the correct service state.

    Source Test Case Purpose: Verify each order status is updated in the orders DB, according to the current order state.

    Source Test Case ID: 18

    Source Test Case Traceability: 2.6
     """
    pass
