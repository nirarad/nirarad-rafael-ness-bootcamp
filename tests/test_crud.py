import time
import unittest
from dotenv import load_dotenv

from utils.testcase.logger import Logger
from utils.api.ordering_api_mocker import OrderingAPI_Mocker
from utils.rabbitmq.eshop_rabbitmq_events import *
from utils.db.db_utils import MSSQLConnector


class TestAP(unittest.TestCase):
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv('.env.test')
        cls.logger = Logger('test', 'Logs/tests.log').logger
        cls.oam = OrderingAPI_Mocker()
        cls.order_uuid = str(uuid.uuid4())
        cls.conn = MSSQLConnector()

    def setUp(self) -> None:
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_create_order(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_create_order
        Description: Function tests Ordering service creation order by RabbitMQ.
                     Function sends message to RabbitMQ queue Ordering to create order,
                     Ordering service have to create order in DB.
                     Validates if order is created and with status.
        """
        try:
            # Save new order id here
            self.new_order_id = None
            # Find last order id to compare if getting right order id,will be   after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            print(last_order_record_in_db)
            # Sending message to RabbitMQ to Ordering queue to create order
            create_order(self.order_uuid)
            # Wait until ordering creates order in DB
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                # if last order updated so it will new order
                if x != last_order_record_in_db:
                    print(last_order_record_in_db)
                    # To pass into loger Actual
                    self.new_order_id = x
                    self.logger.info(
                        f'{self.test_create_order.__doc__}Order Id in DB -> Actual: ID {self.new_order_id} , Expected: {last_order_record_in_db + 1}')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_create_order.__doc__} Order status in DB -> Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)
        except Exception as e:
            self.logger.exception(f"\n{self.test_create_order.__doc__}Actual {e}")
            raise

    def test_cancel_order_v1(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v1
        Description: Function tests Ordering api cancel request when order status is 1 (submitted)
        """
        try:
            # Save new order id here
            self.new_order_id = None
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Sending message to RabbitMQ to Ordering queue to create order
            create_order(self.order_uuid)
            # Wait until ordering creates order in DB
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                if x is None:
                    raise Exception("X is None,Connection lost")
                # if last order updated so it will new order
                if x != last_order_record_in_db:
                    # To pass into loger Actual
                    self.new_order_id = x
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Actual: ID {self.new_order_id} , Expected: Created Order'
                f'Id in DB ')

            # Cancel via mocker the order in status 1 (submitted)

            # Ordering api sends request to cancel order
            y = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 200
            self.assertTrue(y, 200)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Request to cancel status -> Actual:  {y} , Expected:{200}')

            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertTrue(current_order_status, 6)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Order status in DB -> Actual:  {current_order_status} , '
                f'Expected:{6}')
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v1.__doc__}{e}")
            raise

    def test_cancel_order_v2(self):
        """
        Name: Artsyom Sharametsieu
        Date:
        Function Name: test_cancel_order_v2
        Description:
        """
        try:
            # Save new order id here
            self.new_order_id = None
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Sending message to RabbitMQ to Ordering queue to create order
            create_order(self.order_uuid)
            # Wait until ordering creates order in DB
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                if x is None:
                    raise Exception("X is None,Connection lost")
                # if last order updated so it will new order
                if x != last_order_record_in_db:
                    # To pass into loger Actual
                    self.new_order_id = x
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Actual: ID {self.new_order_id} , Expected: Created Order'
                f'Id in DB ')

            # Updating order status in DB to 2
            self.conn.update_order_db_id(self.new_order_id, 2)

            # Validation status changed
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertTrue(current_status, 2)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Order status in DB -> Actual:  {current_status} , Expected:{2}')

            # Cancel via mocker the order in status 1 (submitted)
            # Ordering api sends request to cancel order
            y = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 200
            self.assertTrue(y, 200)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Request to cancel status -> Actual:  {y} , Expected:{200}')

            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertTrue(current_order_status, 6)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Order status in DB -> Actual:  {current_order_status} , '
                f'Expected:{6}')
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v1.__doc__}{e}")
            raise
