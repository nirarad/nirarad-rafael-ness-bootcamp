from shared_imports import *

orderID_of_user_1 = orderingAPI.get_ordernumber_by_username_and_password()

@pytest.mark.security
def test_cancel_order_from_another_user():
    """
    Tests if canceling an order for a different user
    
    """
    assert orderingAPI.cancel_order_by_id(orderID_of_user_1).status_code == 400
    
@pytest.mark.security    
def test_ship_order_from_another_user():
    """
    Tests if shipping an order for a different user
    
    """
    assert orderingAPI.ship_order_by_id(orderID_of_user_1).status_code == 400