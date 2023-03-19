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


class NonFunctionalSuit(unittest.TestCase):
    # Variable of connection to DB
    docker = None
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))
        # Local Logger
        cls.logger = Logger('non_functional_logger', 'Logs/test_non_functional.log').logger
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
        cls.payment_sim = None
        # Catalog simulator
        cls.catalog_sim = None
        # Timeout
        cls.timeout = 720
        # Run common containers and stop not needed
        cls.docker.stop(os.getenv('ORDERING_CONTAINER'))
        cls.docker.start(os.getenv('ORDERING_BACKGROUNDTASKS_CONTAINER'))
        cls.docker.start(os.getenv('RABBITMQ_CONTAINER'))
        cls.docker.start(os.getenv('SQLDATA_CONTAINER'))
        cls.docker.start(os.getenv('IDENTITY_CONTAINER'))
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()

    def setUp(self) -> None:
        # Run common containers
        self.docker.stop(os.getenv('ORDERING_CONTAINER'))
        self.docker.start(os.getenv('ORDERING_BACKGROUNDTASKS_CONTAINER'))
        self.docker.start(os.getenv('RABBITMQ_CONTAINER'))
        self.docker.start(os.getenv('SQLDATA_CONTAINER'))
        self.docker.start(os.getenv('IDENTITY_CONTAINER'))
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()
        # Reconnect
        self.conn.__enter__()
        self.catalog_sim = CatalogSimulator(time_limit=3600)
        self.payment_sim = PaymentSimulator(time_limit=3600)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # TC018
    def test_ordering_service_scalability_100_orders(self):
        """
        TC_ID: TC018
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_ordering_service_scalability_100_orders
        Description: 1.Function tests Ordering service scalability.
                     2.Function validates all order creation.
                     3.Function creating 100 orders and counting time of last order processing.
        """
        try:
            # Amount of orders to create and check
            order_amount = 100
            # Need to know which was last before creating new order
            last_order_id = self.conn.get_last_order_record_id_in_db()
            # 100 orders creation loop
            for i in range(order_amount):
                # Generating new unique x-request id
                order_uuid = str(uuid.uuid4())
                # Message body to send
                message_body = self.jdata_orders.get_json_order('alice_normal_order', order_uuid)
                # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
                self.basket_sim.create_order(message_body)
            # Turn on Ordering api container
            self.docker.start(os.getenv('ORDERING_CONTAINER'))
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
                    # Timeout
                    elif time.time() - start_time > self.timeout:
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
                # Getting current order status
                order_status = self.conn.get_order_status_from_db(order)
                # WAITING UNTIL EACH ORDER WILL BE IN STATUS 4 (paid)
                while order_status != int(os.getenv('PAID')):
                    # Count of time updating
                    time_count_status_2 = 1
                    time_count_status_3 = 1
                    # Checking order status
                    order_status = self.conn.get_order_status_from_db(order)
                    # If order status updates,update time only once
                    if order_status == int(os.getenv('AWAITINGVALIDATION')) and time_count_status_2 > 0:
                        start_time = time.time()
                        time_count_status_2 -= 1
                    elif order_status == int(os.getenv('STOCKCONFIRMED')) and time_count_status_3 > 0:
                        start_time = time.time()
                        time_count_status_3 -= 1
                    # Timeout
                    elif time.time() - start_time > self.timeout:
                        raise Exception("Order status not changed,timeout.")
            # End time of full order creation (to status 4 (paid))
            process_end_time = time.time()
            # Stopping simulators
            self.catalog_sim.time_limit = 0
            self.payment_sim.time_limit = 0
            # Elapsed time of full order creation (to status 4 (paid))
            elapsed_time = process_end_time - process_start_time
            self.assertLessEqual(elapsed_time / 3600, int(os.getenv('SCALABILITY_TIME')))
            self.logger.info(
                f"{self.test_ordering_service_scalability_100_orders.__doc__} "
                f"Order status in DB -> "
                f"Actual: {elapsed_time / 3600} hours , "
                f"Expected: < {int(os.getenv('SCALABILITY_TIME'))} hour/s")
        except Exception as e:
            self.logger.exception(f"\n{self.test_ordering_service_scalability_100_orders.__doc__}{e}")
            raise

    # TC019
    def test_order_api_reliability(self):
        """
        TC_ID: TC019
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_api_reliability
        Description: 1.Function tests Ordering api reliability.
                     2.Function simulates Ordering api crash by stopping his docker container.
                     3.Function sends message to create order to .
        """
        try:
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
            self.docker.start(os.getenv('ORDERING_CONTAINER'))
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
                    self.assertTrue(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f"{self.test_order_api_reliability.__doc__} "
                        f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Time to changing status ended,order status not changed")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_reliability.__doc__}{e}")
            raise


if __name__ == '__main__':
    unittest.main()
