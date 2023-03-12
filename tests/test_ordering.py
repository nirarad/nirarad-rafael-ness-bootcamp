import unittest
import warnings
from utils.docker.docker_utils import *
from utils.MyFunctions import *
from utils.db.db_utils import *
from utils.Simulators.basket_send import Basket_send
from utils.api.ordering_api import OrderingAPI

dm = DockerManager()
env = get_vars()  # Dict of all env vars
ordering_backgroundtasks = env['BACKGROUND']
ordering_api = env['ORDERING_API']
busket_api = env['BUSKET_API']
catalog_api = env['CATALOG_API']
payment_api = env['PAYMENT_API']
scalability_range = env['SCALABILITY_RANGE']


class TestOrdering(unittest.TestCase):

    def test_create_order_when_item_in_stock(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        if dm.is_running(payment_api):
            dm.stop(payment_api)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        dm.start(ordering_backgroundtasks)
        dm.stop(catalog_api)
        if not dm.is_running(ordering_api):
            dm.start(ordering_api)
        # Third Assert - status 2
        self.explicit_wait_status_last_order(60, 2)
        dm.start(catalog_api)
        # Fourth Assert - status 3
        self.explicit_wait_status_last_order(60, 3)
        dm.start(payment_api)
        # Fifth Assert - status 4
        self.explicit_wait_status_last_order(60, 4)
        # Sixth Assert - check update of stock
        self.assertEqual(env['STOCK'] - env['CHOSEN_COUNT'], self.get_stock())
        order_id = self.get_id_of_last_order()
        # Seventh Assert - shipping request - expect status 200
        status_shipping = OrderingAPI().ship_order_by_id(order_id).status_code
        self.assertEqual(200, status_shipping)
        # Eight Assert - status 5
        self.explicit_wait_status_last_order(60, 5)

    def test_create_order_when_item_NOT_in_stock(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['STOCK'] + 1, 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        dm.start(ordering_backgroundtasks)
        dm.stop(catalog_api)
        if not dm.is_running(ordering_api):
            dm.start(ordering_api)
        # Third Assert - status 2
        self.explicit_wait_status_last_order(60, 2)
        dm.start(catalog_api)
        # Fourth Assert - status 3
        self.explicit_wait_status_last_order(60, 6)
        self.assertEqual(env['STOCK'], self.get_stock())

    def test_cancel_when_status_1(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 200
        self.assertEqual(200, status_canceling)
        # Fourth Assert - status 6
        self.explicit_wait_status_last_order(60, 6)

    def test_cancel_when_status_2(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(catalog_api):
            dm.stop(catalog_api)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 2
        self.explicit_wait_status_last_order(60, 2)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 200
        self.assertEqual(200, status_canceling)
        # Fourth Assert - status 6
        self.explicit_wait_status_last_order(60, 6)

    def test_cancel_when_status_3(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(payment_api):
            dm.stop(payment_api)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 3
        self.explicit_wait_status_last_order(60, 3)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 200
        self.assertEqual(200, status_canceling)
        # Fourth Assert - status 6
        self.explicit_wait_status_last_order(60, 6)

    def test_cancel_when_status_4(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 4
        self.explicit_wait_status_last_order(100, 4)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 200
        self.assertEqual(400, status_canceling)
        # Fourth Assert - status still 4
        self.explicit_wait_status_last_order(1, 4)

    def test_cancel_when_status_5(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 4
        self.explicit_wait_status_last_order(100, 4)
        order_id = self.get_id_of_last_order()
        # Third Assert - shipping - expected status 200
        status_shipping = OrderingAPI().ship_order_by_id(order_id).status_code
        self.assertEqual(200, status_shipping)
        # Fourth Assert - status 5
        self.explicit_wait_status_last_order(60, 5)
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Fifth Assert - status canceling - expected 400
        self.assertEqual(400, status_canceling)
        # Sixth Assert - status still 5
        self.explicit_wait_status_last_order(1, 5)

    def test_cancel_when_status_6(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 200
        self.assertEqual(200, status_canceling)
        # Fourth Assert - status 6
        self.explicit_wait_status_last_order(60, 6)
        status_canceling = OrderingAPI().cancel_order_by_id(order_id).status_code
        # Fifth Assert - double canceling - expected status 200
        self.assertEqual(200, status_canceling)
        # Fourth Assert - status still 6
        self.explicit_wait_status_last_order(1, 6)

    def test_ship_to_another_user(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 4
        self.explicit_wait_status_last_order(100, 4)
        # Third Assert - shipping request - expected status 403
        order_id = self.get_id_of_last_order()
        status_shipping = OrderingAPI(username='bob', password='Pass123$').ship_order_by_id(order_id).status_code
        self.assertEqual(403, status_shipping)
        # Fifth Assert - status still 4
        self.explicit_wait_status_last_order(1, 4)

    def test_ship_to_unauthorised_user(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 4
        self.explicit_wait_status_last_order(100, 4)
        # Third Assert - shipping request - expected status 403
        order_id = self.get_id_of_last_order()
        status_shipping = OrderingAPI().ship_order_by_id(order_id, unauthorised=True).status_code
        self.assertEqual(401, status_shipping)
        # Fifth Assert - status still 4
        self.explicit_wait_status_last_order(1, 4)

    def test_cancel_unauthorized(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI().cancel_order_by_id(order_id, unauthorised=True).status_code
        # Third Assert - status canceling - expected 401
        self.assertEqual(401, status_canceling)
        # Fourth Assert - still status 1
        self.explicit_wait_status_last_order(1, 1)

    def test_cancel_with_another_user(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        if dm.is_running(ordering_backgroundtasks):
            dm.stop(ordering_backgroundtasks)
        before_ordering_count = self.get_current_count_orders()
        Basket_send(env['CHOSEN_COUNT'], 'Alice')
        # First Assert - comparing count orders
        self.explicit_wait_on_count_orders(30, before_ordering_count + 1)
        # Second Assert - status 1
        self.explicit_wait_status_last_order(1, 1)
        order_id = self.get_id_of_last_order()
        status_canceling = OrderingAPI(username='bob').cancel_order_by_id(order_id).status_code
        # Third Assert - status canceling - expected 401
        self.assertEqual(403, status_canceling)
        # Fourth Assert - still status 1
        self.explicit_wait_status_last_order(1, 1)

    def test_scalability(self):
        self.start_all_containers()
        self.set_stock(env['STOCK'])
        start_count_orders = self.get_current_count_orders()
        for i in range(scalability_range):
            Basket_send(env['CHOSEN_COUNT'], 'Alice')
        self.explicit_wait_scalability(3600, start_count_orders, scalability_range)

    ### Additional Methods ###
    def set_stock(self, num):
        if num >= 0:
            with MSSQLConnector("CatalogDb") as conn:
                cursor = conn.conn.cursor()
                cursor.execute(f'update Catalog set AvailableStock={num} where Id=1')
                conn.conn.commit()
        else:
            warnings.warn(f"Unable to set number {num}")

    def get_stock(self):
        with MSSQLConnector("CatalogDb") as conn:
            return conn.select_query('SELECT AvailableStock from Catalog')[0]['AvailableStock']

    def get_current_count_orders(self):
        with MSSQLConnector() as conn:
            res = conn.select_query('SELECT * from ordering.orders')
            return len(res)

    def get_id_of_last_order(self):
        with MSSQLConnector() as conn:
            return conn.select_query('SELECT * from ordering.orders order by id desc')[0]['Id']

    def get_status_of_last_order(self):
        with MSSQLConnector() as conn:
            return conn.select_query('SELECT * from ordering.orders order by id desc')[0]['OrderStatusId']

    def explicit_wait_on_count_orders(self, sec, expected_count):
        while sec != 0:
            if expected_count == self.get_current_count_orders():
                return
            time.sleep(1)
            sec -= 1
        self.assertEqual(expected_count, self.get_current_count_orders())

    def explicit_wait_status_last_order(self, sec, expected_status):
        while sec != 0:
            if expected_status == self.get_status_of_last_order():
                return
            time.sleep(1)
            sec -= 1
        self.assertEqual(expected_status, self.get_status_of_last_order())

    def start_all_containers(self):
        for container in dm.containers:
            container.start()

    def explicit_wait_scalability(self, sec, start_count, range):
        while sec > 0:
            current_count_orders = self.get_current_count_orders()
            if current_count_orders == start_count + scalability_range:
                with MSSQLConnector() as conn:
                    res = (conn.select_query(
                        f'select * from (SELECT top {range} * from ordering.orders order by id desc) as T where OrderStatusId=4'))
                    if len(res) == range:
                        return
            time.sleep(60)
            sec -= 60
        self.assert_(False, msg="Time is up, test Scalability failed")
