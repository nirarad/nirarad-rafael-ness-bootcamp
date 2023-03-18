from shared_imports import *

@pytest.mark.preformance    
def test_server_crashes_before_each_of_the_steps_mss():
    """
    Tests system behavior when the server crashes
    before each step of the order process.
    Verifies system recovery and continuation to next step.  
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    # step 1: Stop and start the reservation server,
    # Create an order and remove items from the basket.
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    # step 2: Stop and start the reservation server,
    # Start the ordering background service and verify the items are in stock.
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
    
    # step 3: Stop and start the reservation server, 
    # Confirm the item inventory and verify that the payment succeeded.
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 4: Stop and start the reservation server, 
    # Verify that the order status is set to "4".
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4

@pytest.mark.preformance
def test_crashes_before_step_1_mss():
    """
    Tests system behavior when the server crashes
    before step 1
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Stop and start the reservation server
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    
    #step 2: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 3: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
    
    # step 4: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 5: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
@pytest.mark.preformance    
def test_crashes_before_step_2_mss():
    """
    Tests system behavior when the server crashes
    before step 2
    
    """
    dm.stop(os.getenv('ORDERING_BACKGROUND'))
    
    #step 1: Create an order and remove items from the basket.
    basket.create_order()
    assert queries.get_status(4,1) == 1
    assert basket.remove_items_form_basket() == True
    
    #step 2: Stop and start the reservation server
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    
    #step 3: Start the ordering background service and verify the items are in stock.
    dm.start(os.getenv('ORDERING_BACKGROUND'))
    assert queries.get_status(1,2) == 2
    assert catalog.verify_item_in_stock() == True
    
    # step 4: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 5: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
@pytest.mark.preformance    
def test_crashes_before_step_3_mss():
    """
    Tests system behavior when the server crashes
    before step 3
    
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
    
    #step 3: Stop and start the reservation server
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    
    # step 4: Confirm the item inventory and verify that the payment succeeded.
    catalog.item_in_stock()
    assert queries.get_status(2,3) == 3
    assert payment.order_inventory_confirmed() == True
    
    #step 5: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
@pytest.mark.preformance    
def test_crashes_before_step_4_mss():
    """
    Tests system behavior when the server crashes
    before step 4
    
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
    
    #step 4: Stop and start the reservation server
    dm.stop(os.getenv('ORDERING'))
    dm.start(os.getenv('ORDERING'))
    
    #step 5: Verify that the order status is set to "4".
    payment.payment_succeeded()
    assert queries.get_status(3,4) == 4
    
   