import os
import time
import unittest
import uuid

from dotenv import load_dotenv
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import create_order
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger


class TestScalability(unittest.TestCase):
    # Variable of connection to DB
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv('DATA/.env.test')

        # Local Logger
        cls.logger = Logger('scalability_logger', 'Logs/test_scalability.log').logger

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
                     3.Function creating 100 orders and counting time of creations.
        """
        try:
            loop_start_time = time.time()
            for i in range(100):
                # Generating new unique x-request id
                order_uuid = str(uuid.uuid4())
                # Find last order id to compare if getting right order id,will be pre last after creating new order
                last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
                # Message body to send
                message_body = self.jdata_orders.get_json_order('alice_normal_order', order_uuid)
                # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
                create_order(message_body)
                # Wait until ordering creates order in DB
                start_time = time.time()
                while True:
                    # Getting last order id
                    x = self.conn.get_last_order_record_id_in_db()
                    # if last order updated so it will be new order
                    if x != last_order_record_in_db:
                        # To pass into loger Actual
                        self.new_order_id = x
                        self.logger.info(
                            f'{self.test_order_api_scalability_100_orders.__doc__}'
                            f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                            f'Expected: New Order Id')
                        # Validate status order is 1
                        current_status = self.conn.get_order_status_from_db(self.new_order_id)
                        self.assertTrue(current_status, 1)
                        self.logger.info(
                            f'{self.test_order_api_scalability_100_orders.__doc__} '
                            f'Order status in DB -> Actual: {current_status} , Expected: {1}')
                        break
                    # if 10 sec pass no sense to wait
                    elif time.time() - start_time > 10:  # Timeout after 10 seconds
                        raise Exception("Record was not created")
                    # Updating timer
                    time.sleep(0.1)

            loop_end_time = time.time()
            # Creation of 100 orders time
            elapsed_time = loop_end_time - loop_start_time
            self.assertLessEqual(elapsed_time, 100)
            self.logger.info(
                f'{self.test_order_api_scalability_100_orders.__doc__} '
                f'Order status in DB -> Actual: {elapsed_time / 3600} hours , Expected: < {100} hours')
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_scalability_100_orders.__doc__}Actual {e}")
            raise


if __name__ == '__main__':
    unittest.main()
