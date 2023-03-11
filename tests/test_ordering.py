import time
import unittest
import warnings
import docker
from utils.docker.docker_utils import *
from utils.MyFunctions import *
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.db.db_utils import *
from utils.Simulators.basket_send import Basket_send
from utils.api.ordering_api import *
import uuid
import json
import datetime

dm = DockerManager()
env = get_vars() # Dict of all env vars
ordering_backgroundtasks = env['BACKGROUND']
ordering_api = env['ORDERING_API']
busket_api = env['BUSKET_API']
catalog_api = env['CATALOG_API']
payment_api = env['PAYMENT_API']


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
        self.explicit_wait_on_count_orders(30,before_ordering_count+1)
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
        self.assertEqual(env['STOCK']-env['CHOSEN_COUNT'], self.get_stock())
        op = OrderingAPI()
        op.ship_order_by_id()


    def set_stock(self,num):
        if num>=0:
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

    def get_status_of_last_order(self):
        with MSSQLConnector() as conn:
            return conn.select_query('SELECT * from ordering.orders order by id desc')[0]['OrderStatusId']

    def explicit_wait_on_count_orders(self, sec, expected_count):
        while sec!=0:
            if expected_count==self.get_current_count_orders():
                return
            time.sleep(1)
            sec-=1
        self.assertEqual(expected_count,self.get_current_count_orders())

    def explicit_wait_status_last_order(self, sec, expected_status):
        while sec!=0:
            if expected_status==self.get_status_of_last_order():
                return
            time.sleep(1)
            sec-=1
        self.assertEqual(expected_status,self.get_status_of_last_order())

    def start_all_containers(self):
        for container in dm.containers:
            container.start()