import os
import time
import unittest
import uuid

from dotenv import load_dotenv
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import create_order
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ


class TestScalability(unittest.TestCase):
    # Variable of connection to DB
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv('DATA/.env.test')

        # Local Logger
        cls.logger = Logger('non_functional_logger', 'Logs/test_non_functional.log').logger

        # Unique id generator
        cls.order_uuid = str(uuid.uuid4())

        # Connection to DB
        cls.conn = MSSQLConnector()

        # Order Id saver
        cls.new_order_id = None

        # Json Data Order handler
        cls.jdata_orders = JSONDataReader(os.getenv('ORDERS_PATH'))

        # Last order created
        cls.last_order = None

        # Docker manager
        cls.docker = DockerManager()

    def setUp(self) -> None:
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # TC017
    def test_order_api_scalability_100_orders(self):
        """
        TC_ID: TC017
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_api_scalability_100_orders
        Description: 1.Function tests Ordering api scalability.
                     2.Function validates all order creation.
                     3.Function creating 100 orders and counting time of last order processing.
        """
        try:
            last_order_id = self.conn.get_last_order_record_id_in_db()
            # Clean messages from previous using of RabbitMQ queue
            with RabbitMQ() as mq:
                mq.purge('Ordering')
            # Pausing ordering api container to load Ordering queue
            self.docker.stop('eshop/ordering.api:linux-latest')
            # 100 orders creation loop
            for i in range(100):
                # Generating new unique x-request id
                order_uuid = str(uuid.uuid4())
                # Message body to send
                message_body = self.jdata_orders.get_json_order('alice_normal_order', order_uuid)
                # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
                create_order(message_body)

            # Turn on Ordering api container and Ordering BackgroundTasks container
            self.docker.start('eshop/ordering.api:linux-latest')
            self.docker.start('eshop/ordering.backgroundtasks:linux-latest')
            # Handler to save all created order ids to check statuses after
            order_ids = []
            # Searching for all 100 order ids
            for i in range(100):
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
                            f'{self.test_order_api_scalability_100_orders.__doc__}'
                            f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                            f'Expected: New Order Id')
                        break
                    # if 15 sec pass no sense to wait
                    elif time.time() - start_time > 15:  # Timeout after 15 seconds
                        raise Exception("Record was not created")

            # Check for all 100 orders status
            for i in range(100):
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
                            f'{self.test_order_api_scalability_100_orders.__doc__}'
                            f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                            f'Expected: New Order Id')
                        break
                    # if 15 sec pass no sense to wait
                    elif time.time() - start_time > 15:  # Timeout after 15 seconds
                        raise Exception("Record was not created")
            # # Starting count of processing of all orders
            # loop_start_time = time.time()
            # loop_end_time = time.time()
            # # Creation of 100 orders time
            # elapsed_time = loop_end_time - loop_start_time
            # self.assertLessEqual(elapsed_time, 100)
            # self.logger.info(
            #     f'{self.test_order_api_scalability_100_orders.__doc__} '
            #     f'Order status in DB -> Actual: {elapsed_time / 3600} hours , Expected: < {100} hours')
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_scalability_100_orders.__doc__} Error:{e}")
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
            create_order(message_body)
            # Running order api docker container
            self.docker.start('eshop/ordering.api:linux-latest')
            # Wait for creation of order,exit when be found or timeout
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
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 15:  # Timeout after 15 seconds
                    raise Exception("Record was not created")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_reliability.__doc__} Error:{e}")
            raise


if __name__ == '__main__':
    unittest.main()
