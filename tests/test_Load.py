from shared_imports import *
import time
from datetime import timedelta


@pytest.mark.load    
def test_Check_loads_on_creating_an_order():
    """
    Test if it is possible to produce 100 orders per hour.

    """
    before = 0
    after = 0
    time_before = time.time()
    before = queries.count_order()
    
    for i in range(100):
        basket.create_order() 
        basket.remove_items_form_basket()
        catalog.verify_item_in_stock()         
        catalog.item_in_stock()    
        payment.order_inventory_confirmed()
        payment.payment_succeeded()

      
    after = queries.count_order()
    assert before + 100 == after   
    assert time_before - time.time() == timedelta(hours=1)    
