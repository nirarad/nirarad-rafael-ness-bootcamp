import os
import threading
import time
import unittest
import uuid

from utils.db.db_utils import MSSQLConnector
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from simulators.basket_simulator import BasketSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.payment_simulator import PaymentSimulator

from dotenv import load_dotenv


class TestScalability(unittest.TestCase):
    # Variable of connection to DB
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv('../.env.test')

        # Local Logger
        cls.logger = Logger('non_functional_logger', 'Logs/test_non_functional.log').logger

        # Unique id generator
        cls.order_uuid = str(uuid.uuid4())

        # Connection to DB
        cls.conn = MSSQLConnector()

        # Order Id saver
        cls.new_order_id = None

        # Json Data Order handler
        cls.jdata_orders = JSONDataReader('DATA/ORDERS_DATA.json')

        # Last order created
        cls.last_order = None

        # Docker manager
        cls.docker = DockerManager()

        # Basket Simulator
        cls.basket_sim = BasketSimulator()

        # Payment simulator
        cls.payment_sim = PaymentSimulator(time_limit=300)

        # Catalog simulator
        cls.catalog_sim = CatalogSimulator(time_limit=300)

    def setUp(self) -> None:
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # TC017
    def test_ordering_service_scalability_100_orders(self):
        """
        TC_ID: TC017
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_ordering_service_scalability_100_orders
        Description: 1.Function tests Ordering service scalability.
                     2.Function validates all order creation.
                     3.Function creating 100 orders and counting time of last order processing.
        """
        try:
            # Amount of orders to create and check
            order_amount = 2
            # Stopping ordering api and ordering.backgroundtasks containers to load Ordering queue
            self.docker.stop('eshop/ordering.api:linux-latest')
            self.docker.stop('eshop/ordering.backgroundtasks:linux-latest')

            # Need to know which was last before creating new order
            last_order_id = self.conn.get_last_order_record_id_in_db()

            # Clean messages from previous using of RabbitMQ queue
            with RabbitMQ() as mq:
                mq.purge('Ordering')
                mq.purge('Catalog')
                mq.purge('Payment')
            # 100 orders creation loop
            for i in range(order_amount):
                # Generating new unique x-request id
                order_uuid = str(uuid.uuid4())
                # Message body to send
                message_body = self.jdata_orders.get_json_order('alice_normal_order', order_uuid)
                # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
                self.basket_sim.create_order(message_body)

            # Turn on Ordering api container and Ordering BackgroundTasks container
            self.docker.start('eshop/ordering.api:linux-latest')
            self.docker.start('eshop/ordering.backgroundtasks:linux-latest')
            # Handler to save all created orders id to check statuses after
            order_ids = []
            # Start time of full order creation (to status 4 (paid))
            process_start_time = time.time()
            # Searching for all 100 order ids in DB
            for i in range(order_amount):
                start_time = time.time()
                while True:
                    # Getting last order id
                    x = self.conn.get_next_order_id(last_order_id)
                    # if last order updated so it will be new order
                    if x is not None and x != last_order_id:
                        # To pass into loger Actual
                        order_ids.append(x)
                        last_order_id = x
                        self.logger.info(
                            f'{self.test_ordering_service_scalability_100_orders.__doc__}'
                            f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                            f'Expected: New Order Id')
                        break
                    # if 15 sec pass no sense to wait
                    elif time.time() - start_time > 60:  # Timeout after 60 seconds
                        raise Exception("Order was not created")

            # INCLUDING SIMULATORS TO FULL ORDER CREATION FLOW
            # Threads will close by self after time (not does not affect on order creation time)
            catalog_thread = threading.Thread(target=self.catalog_sim.consume_to_confirm_stock)
            payment_thread = threading.Thread(target=self.payment_sim.consume_to_succeed_payment)
            catalog_thread.start()
            payment_thread.start()
            # Check for all 100 orders status
            for order in order_ids:
                start_time = time.time()
                # WAITING UNTIL EACH ORDER WILL BE IN STATUS 4 (paid)
                while self.conn.get_order_status_from_db(order) != 4:
                    # Getting last order id
                    x = self.conn.get_next_order_id(last_order_id)
                    # if last order updated, so it will be new order
                    if x is not None and x != last_order_id:
                        # To pass into loger Actual
                        order_ids.append(x)
                        last_order_id = x
                        self.logger.info(
                            f'{self.test_ordering_service_scalability_100_orders.__doc__}'
                            f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                            f'Expected: New Order Id')
                        break
                    elif time.time() - start_time > 400:  # Timeout after 5 minutes
                        raise Exception("Order status not changed,timeout.")
            # End time of full order creation (to status 4 (paid))
            process_end_time = time.time()
            # Elapsed time of full order creation (to status 4 (paid))
            elapsed_time = process_end_time - process_start_time
            self.assertLessEqual(elapsed_time / 3600, 1)
            self.logger.info(
                f'{self.test_ordering_service_scalability_100_orders.__doc__} '
                f'Order status in DB -> Actual: {elapsed_time / 3600} hours , Expected: < {1} hour/s')
        except Exception as e:
            self.logger.exception(f"\n{self.test_ordering_service_scalability_100_orders.__doc__} Error:{e}")
            raise

        # TC017

    def test_order_api_reliability(self):
        """
        TC_ID: TC018
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_api_reliability
        Description: 1.Function tests Ordering api reliability.
                     2.Function simulates Ordering api crash by stopping his docker container.
                     3.Function sends message to create order to .
        """
        try:
            # Clean messages from previous using of RabbitMQ queue
            with RabbitMQ() as mq:
                mq.purge('Ordering')
            # Pausing ordering api container to load Ordering queue
            self.docker.stop('eshop/ordering.api:linux-latest')
            # Handler to save all created order ids to check statuses after
            # Generating new unique x-request id
            order_uuid = str(uuid.uuid4())
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            self.basket_sim.create_order(message_body)
            # Running order api docker container
            self.docker.start('eshop/ordering.api:linux-latest')
            # Wait until order status changed
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                # if last order updated so it will be new order
                if x != last_order_record_in_db:
                    # To pass into loger Actual
                    self.new_order_id = x
                    self.logger.info(
                        f'{self.test_order_api_reliability.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_order_api_reliability.__doc__} '
                        f'Order status in DB -> Actual: {current_status} , Expected: {1}')
                    break
                # if 60 sec pass no sense to wait
                elif time.time() - start_time > 60:  # Timeout after 15 seconds
                    raise Exception("Time to changing status ended,order status not changed")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_reliability.__doc__} Error:{e}")
            raise


if __name__ == '__main__':
    unittest.main()
