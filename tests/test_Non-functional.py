from shared_imports import *

@pytest.mark.nonfunctional    
def test_Cancel_an_order_with_paid_status():
    """
    Tests canceling an order with "paid" status.

    Asserts:
     - The cancellation attempt returns a status code of 400.
     - The order status remains unchanged at 4.
     """
    
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
        
    # #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
        
    # step 3: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
        
    #step 4: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
    
    assert orderingAPI.cancel_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(6,4) == 4
    
@pytest.mark.nonfunctional      
def test_Cancel_an_order_with_shipped_status():
    """
    Tests canceling an order with "shipped" status.
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
        
    # #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
        
    # step 3: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
        
    #step 4: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
    # Ship the order.
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 200
    assert queries.get_status(4,5) == 5
    
    # Attempt to cancel the order and verify the system behavior.
    assert orderingAPI.cancel_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(6,5) == 5
  
@pytest.mark.nonfunctional       
def test_get_order_by_non_exist_id():
    """
    Tests retrieving an order by a non-existent ID.

    Asserts:
    - The attempt to retrieve the order returns a status code of 404.
    """
    assert orderingAPI.get_order_by_id(0).status_code == 404
 
@pytest.mark.nonfunctional    
def test_ship_Order_with_Cancelled_status():
    """
    Tests shipping an order with "cancelled" status.
    
    Asserts:
    - The shipping attempt returns a status code of 400.
    - The order status remains unchanged at 6.
    """ 
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
    
    # step 3: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True

    #step 4: Cancel the order.
    orderingAPI.cancel_order_by_id(queries.get_last_ordering())
    assert queries.get_status(3,6) == 6
    
    # Attempt to ship the order and verify the system behavior.
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(5,6) == 6
    
@pytest.mark.nonfunctional    
def test_ship_Order_with_stockconfirmed_status():   
    """
    Tests shipping an order with "stockconfirmed" status.
    
    Asserts:
    - The shipping attempt returns a status code of 400.
    - The order status remains unchanged at 3.    
    """
    
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
    
    # step 3: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 4: Attempt to ship the order and verify the system behavior.
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(5,3) == 3
    
@pytest.mark.nonfunctional    
def test_ship_Order_with_submitted_status():
    """
    Tests shipping an order with "submitted" status.
    
    Asserts:
    - The shipping attempt returns a status code of 400.
    - The order status remains unchanged at 1.
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True    
    
    #step 2: Attempt to ship the order and verify the system behavior.
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(5,1) == 1
    
@pytest.mark.nonfunctional    
def test_ship_Order_with_awaitingvalidation_status():   
    """
    Tests shipping an order with awaiting-validation status.

    Asserts:
    - The shipping attempt returns a status code of 400.
    - The order status remains unchanged at 2.
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
     
    
    #step 3:  Attempt to ship the order and verify the system behavior.
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 400
    assert queries.get_status(5,2) == 2