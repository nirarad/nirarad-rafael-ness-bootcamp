import os
import unittest
import uuid
import time

from dotenv import load_dotenv

from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.testcase.logger import Logger
from utils.api.ordering_api_mocker import OrderingAPI_Mocker
from utils.db.db_utils import MSSQLConnector
from utils.testcase.jsondatareader import JSONDataReader
from simulators.basket_simulator import BasketSimulator


class SecuritySuit(unittest.TestCase):
    # Tests of creation,cancel and getting order

    # Handler of connection to DB
    docker = None
    conn = None

    # Init of class TestCrud
    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))
        # Docker manager
        cls.docker = DockerManager()
        # Local Logger
        cls.logger = Logger('security_logger', 'Logs/test_security.log').logger
        # Ordering API mocker,user Alice
        cls.oam_alice = OrderingAPI_Mocker('Alice', 'Pass123%24')
        # Ordering API mocker,user Bob
        cls.oam_bob = OrderingAPI_Mocker('Bob', 'Pass123$')
        # Unique id generator handler
        cls.order_uuid = None
        # Connection to DB
        cls.conn = MSSQLConnector()
        # Order Id saver
        cls.new_order_id = None
        # Basket Simulator
        cls.basket_sim = BasketSimulator()
        # Json Data Order handler
        cls.jdata_orders = JSONDataReader('DATA/ORDERS_DATA.json')
        # Timeout
        cls.timeout = 300
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()

    def setUp(self) -> None:
        # Run common containers
        self.docker.stop(os.getenv('ORDERING_BACKGROUNDTASKS_CONTAINER'))
        self.docker.start(os.getenv('RABBITMQ_CONTAINER'))
        self.docker.start(os.getenv('SQLDATA_CONTAINER'))
        self.docker.start(os.getenv('ORDERING_CONTAINER'))
        self.docker.start(os.getenv('IDENTITY_CONTAINER'))
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()
        # Reconnect
        self.conn.__enter__()
        # Unique id of order
        self.order_uuid = str(uuid.uuid4())

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # TC016
    def test_get_order_with_other_user_token(self):
        """
        TC_ID: TC016
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_get_order_with_other_user_token
        Description: 1.Creates normal order of Alice.
                     2.Validates order created.
                     3.Sends REST API request by bob to get Alice order.
                     4.Validates response status.
        """

        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order
            self.basket_sim.create_order(message_body)
            # Explicit wait until ordering creates order in DB
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                # if last order updated so it will be new order
                if x != last_order_record_in_db:
                    # To pass into loger Actual
                    self.new_order_id = x
                    self.logger.info(
                        f'{self.test_get_order_with_other_user_token.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id} , '
                        f'Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f'{self.test_get_order_with_other_user_token.__doc__} '
                        f"Order status in DB -> Actual: {current_status} , "
                        f"Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Validating response status
            response = self.oam_bob.get_order_by_id(self.new_order_id)
            self.assertEqual(400, response.status_code)
            self.logger.info(
                f'{self.test_get_order_with_other_user_token.__doc__} '
                f"Order status in DB -> Actual: {response.status_code} , Expected: {400}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_get_order_with_other_user_token.__doc__}{e}")
            raise

    # TC017
    def test_cancel_order_with_other_user_token(self):
        """
        TC_ID: TC017
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_with_other_user_token
        Description: 1.Creates normal order of Alice.
                     2.Validates order created.
                     3.Sends REST API request by bob to cancel Alice order.
                     4.Validates response status.
                     5.Validates order status didn't change to 6 (cancelled)
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order
            self.basket_sim.create_order(message_body)
            # Explicit wait until ordering creates order in DB
            start_time = time.time()
            while True:
                # Getting last order id
                x = self.conn.get_last_order_record_id_in_db()
                # if last order updated so it will be new order
                if x != last_order_record_in_db:
                    # To pass into loger Actual
                    self.new_order_id = x
                    self.logger.info(
                        f'{self.test_cancel_order_with_other_user_token.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id} , '
                        f'Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(current_status, int(os.getenv('SUBMITTED')))
                    self.logger.info(
                        f'{self.test_cancel_order_with_other_user_token.__doc__} '
                        f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Validating response status
            response_status = self.oam_bob.cancel_order(self.new_order_id, self.order_uuid)
            self.assertEqual(400, response_status.status_code)
            self.logger.info(
                f'{self.test_cancel_order_with_other_user_token.__doc__} '
                f"Order status in DB -> Actual: {response_status.status_code} , Expected: {400}")
            # Validating order status in DB
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('SUBMITTED')))
            self.logger.info(
                f'{self.test_cancel_order_with_other_user_token.__doc__} '
                f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_with_other_user_token.__doc__}{e}")
            raise
