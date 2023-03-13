from tests.scenarios.scenarios import *


@pytest.mark.payment_processing
def test_payment_validation_process():
    """
    Source Test Case Title: Verify that the order process continues whenever the payment process has succeeded.

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 19

    Source Test Case Traceability: 3.1
     """
    # Run step 1
    test_order_submission_scenario()
    # Run Steps 2-3
    test_catalog_stock_confirmation_scenario()
    # Run Steps 4-5
    test_payment_confirmation_scenario()


@pytest.mark.payment_processing
def test_payment_rejection_process(purge_all_queues):
    """
    Source Test Case Title: Verify that the order is canceled whenever the payment process has failed.

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 20

    Source Test Case Traceability: 3.2
     """
    # Run step 1
    test_order_submission_scenario()
    # Run Steps 2-3
    test_catalog_stock_confirmation_scenario()
    # Run Steps 4-5
    test_payment_confirmation_scenario()


@pytest.mark.payment_processing
@pytest.mark.canceling_order
def test_payment_process_rejection_caused_by_server_timeout(purge_all_queues):
    """
    Source Test Case Title: Validate that the service will cancel the ordering process when the service is on ‘confirmstock’ status and the user does not initiate any action for 1 hour.

    Source Test Case Purpose: Verify that the integration with the payment service and its queue are working.

    Source Test Case ID: 21

    Source Test Case Traceability: 3.3
    """
    pass
