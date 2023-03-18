import pytest

from tests.scenarios.scenarios import *
from config.constants import *


@pytest.mark.order_management
@pytest.mark.main_success_scenario
def test_mss():
    """
    Source Test Case Title: Verify the main success scenario for creating order is valid.

    Source Test Case Purpose: Verify that the submitting order functionality of the service is working.

    Source Test Case ID:1

    Source Test Case Traceability: 1.1.1
    """
    # Run steps 1-2
    assert order_submission_scenario()
    # Run steps 3-5
    assert catalog_stock_confirmation_scenario()
    # Run steps 5-6
    assert payment_confirmation_scenario()
    # Run step 7
    assert ship_api_request_scenario()


@pytest.mark.order_management
@pytest.mark.creating_order
def test_user_can_submit_an_order():
    """
    Source Test Case Title: Verify that the user can submit an order.

    Source Test Case Purpose: Verify that the submitting order functionality of the service is working.

    Source Test Case ID: 2

    Source Test Case Traceability: 1.2.1
    """
    # Run Step 1
    assert order_submission_scenario()


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_1():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘submitted’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 1.

    Source Test Case ID: 3

    Source Test Case Traceability: 1.3.1, 5.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert cancel_api_request_scenario()


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_2():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘awaitingvalidation’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 2.

    Source Test Case ID: 4

    Source Test Case Traceability: 1.3.2, 5.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2 - Verify that the catalog queue received from the ordering service the correct message.
    assert EShopSystem.explicit_status_id_validation(status_id=AWAITING_VALIDATION_STATUS, timeout=300)
    # Run step 3
    assert cancel_api_request_scenario()


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_cancel_order_on_status_3():
    """
    Source Test Case Title: Verify that the user can cancel his order when the order status is ‘stockconfirmd’.

    Source Test Case Purpose:  Verify that the canceling order functionality of the microservice is working on order status number 3.

    Source Test Case ID: 5

    Source Test Case Traceability: 1.3.3, 5.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert catalog_stock_confirmation_scenario()
    # Run step 3
    assert cancel_api_request_scenario()


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_not_cancel_order_on_status_4():
    """
    Source Test Case Title:Verify that the user can not cancel his order when the order status is ‘paid’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 4.

    Source Test Case ID: 6

    Source Test Case Traceability: 1.3.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run Steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run Steps 4-5
    assert payment_confirmation_scenario()
    # Run step 6
    assert cancel_api_request_scenario(status_code=400, timeout=100)
    assert EShopSystem.explicit_status_id_validation(status_id=PAID_STATUS, timeout=100)


@pytest.mark.order_management
@pytest.mark.canceling_order
def test_user_can_not_cancel_order_on_status_5():
    """
    Source Test Case Title: Verify that the user can not cancel his order when the order status is ‘paid’.

    Source Test Case Purpose: Verify that the canceling order functionality of the microservice is working on order status number 5.

    Source Test Case ID: 7

    Source Test Case Traceability: 1.3.5
    """
    # Run step 1
    assert order_submission_scenario()
    # Run steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run steps 4-5
    assert payment_confirmation_scenario()
    # Run step 6
    assert ship_api_request_scenario()
    # Run step 7
    assert cancel_api_request_scenario(status_code=400)
    assert EShopSystem.explicit_status_id_validation(status_id=SHIPPED_STATUS, timeout=100)


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_ship_order_on_status_4():
    """
    Source Test Case Title: Verify that the service allows updating order status to ‘shipped’ from ‘paid’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (updating the status) on order status number 4.

    Source Test Case ID: 8

    Source Test Case Traceability: 1.4.1, 5.5
    """
    # Run step 1
    assert order_submission_scenario()
    # Run steps 2-3
    assert catalog_stock_confirmation_scenario()
    # Run steps 4-5
    assert payment_confirmation_scenario()
    # Run step 6
    assert ship_api_request_scenario()


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_1():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to ‘shipped’ from ‘submitted’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status)  on order status number 1.

    Source Test Case ID: 9

    Source Test Case Traceability: 1.4.2
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert ship_api_request_scenario(status_code=400)


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_2():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to ‘shipped’ from ‘awatingvalidation’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 2.

    Source Test Case ID: 10

    Source Test Case Traceability: 1.4.3
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert EShopSystem.explicit_status_id_validation(status_id=AWAITING_VALIDATION_STATUS, timeout=100)
    # Run step 3
    assert ship_api_request_scenario(status_code=400)
    assert EShopSystem.explicit_status_id_validation(status_id=AWAITING_VALIDATION_STATUS, timeout=100)


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_3():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to  ‘shipped’  from ‘stockconfirmd’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 3.

    Source Test Case ID: 11

    Source Test Case Traceability: 1.4.4
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert catalog_stock_confirmation_scenario()
    # Run step 3
    assert ship_api_request_scenario(400)
    # Run step 4
    assert EShopSystem.explicit_status_id_validation(status_id=STOCK_CONFIRMED_STATUS, timeout=100)


@pytest.mark.order_management
@pytest.mark.ship_order
def test_user_can_not_ship_order_on_status_6():
    """
    Source Test Case Title: Verify that the service does not allow updating the order status to ‘shipped’ from ‘canceled’ status.

    Source Test Case Purpose: Verify that the updating order functionality of the microservice is working (not updating the status) on order status number 6.

    Source Test Case ID: 12

    Source Test Case Traceability: 1.4.5
    """
    # Run step 1
    assert order_submission_scenario()
    # Run step 2
    assert cancel_api_request_scenario()
    # Run step 3
    assert ship_api_request_scenario(400)
    assert EShopSystem.explicit_status_id_validation(status_id=CANCELED_STATUS, timeout=50)
