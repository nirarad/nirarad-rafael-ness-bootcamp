import time

from Utils.DB.db_utils import MSSQLConnector

def select_orders_by_buyer_id(buyer_id):
    with MSSQLConnector() as conn:
        orders = conn.select_query(f'SELECT * FROM ordering.orders WHERE buyerId = {buyer_id}')
    return orders

def select_last_order():
    with MSSQLConnector() as conn:
        last_order = conn.select_query('SELECT * FROM ordering.orders ORDER BY id DESC')[0]
    return last_order

def select_last_order_status():
    with MSSQLConnector() as conn:
        status_id = conn.select_query('SELECT * FROM ordering.orders ORDER BY id DESC')[0]['OrderStatusId']
    return status_id

def select_orders_count():
    with MSSQLConnector() as conn:
        order_count = conn.select_query('SELECT COUNT(*) AS count FROM ordering.orders')[0]['count']
    return order_count

def verify_latest_order_status_id(expected_id, timeout=300) -> bool:
    with MSSQLConnector() as conn:
        for i in range(0, timeout, 5):
            status_id = conn.select_query('SELECT * FROM ordering.orders ORDER BY id DESC')[0]['OrderStatusId']
            if (status_id == expected_id):
                return True
            else:
                time.sleep(5)
    return False