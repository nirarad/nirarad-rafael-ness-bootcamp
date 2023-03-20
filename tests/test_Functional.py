
from shared_imports import *

@pytest.mark.functional    
def test_mss():
    """
    Test the complete order creation process with successful payment.

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

@pytest.mark.functional         
def test_Create_Order_with_failed_payment():
    """
    Test the order creation process with payment failure.

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
    
    # step 3: Confirm the item inventory and verify that the payment failed.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 4: Verify that the order status is set to "6".
    payment.payment_failed()
    assert queries.get_status(3,6) == 6

@pytest.mark.functional    
def test_Create_Order_with_outOfStock_items():
    """
    Test the order creation process with out-of-stock items.
   
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
    
    #step 3: Find one or more items out of stock, verify that the order status is set to "6".
    catalog.item_out_of_stock()
    assert queries.get_status(2,6) == 6
    
@pytest.mark.functional        
def test_Cancel_an_order_with_stockconfirmed_status():
    """
    Test the cancellation of an order with "stock confirmed" status.
    
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

    #step 4: Cancel the order, verify that the order status is set to "6".
    orderingAPI.cancel_order_by_id(queries.get_last_ordering())
    assert queries.get_status(3,6) == 6

@pytest.mark.functional    
def test_Cancel_an_order_with_awaitingvalidation_status():
    """
    Test the cancellation of an order with "awaiting validation" status.
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4, 1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 2: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True

    #step 3: Cancel the order, verify that the order status is set to "6".
    orderingAPI.cancel_order_by_id(queries.get_last_ordering())
    assert queries.get_status(2,6) == 6
    
@pytest.mark.functional    
def test_Cancel_an_order_with_submitted_status():
    """
    Test the cancellation of an order with "submitted" status.
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True

    #step 2: Cancel the order, verify that the order status is set to "6".
    assert orderingAPI.cancel_order_by_id(queries.get_last_ordering()).status_code == 200
    assert queries.get_status(1,6) == 6

@pytest.mark.functional    
def test_get_order_by_id():
    """
    Test the retrieval of an order by its ID.

    This test verifies that the order retrieval endpoint returns a HTTP 200 status code.

    """
    assert orderingAPI.get_order_by_id(queries.get_last_ordering()).status_code == 200
    
@pytest.mark.functional        
def test_get_orders():
    """
    Test the retrieval of all orders.

    This test verifies that the orders retrieval endpoint returns a HTTP 200 status code.

    """
    assert orderingAPI.get_orders().status_code == 200
    
@pytest.mark.functional        
def test_ship_an_order_with_paid_status():
    """
    Tests if a paid order can be shipped successfully.
    
    Calls test_mss() and asserts that the ship_order_by_id() 
    returns a status code of 200
    and the order status is updated to 5 in the database.
    """
    test_mss()
    assert orderingAPI.ship_order_by_id(queries.get_last_ordering()).status_code == 200
    assert queries.get_status(4, 5) == 5