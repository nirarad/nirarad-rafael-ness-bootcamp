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


class TestCrud(unittest.TestCase):
    # Tests of creation,cancel and getting order

    # Handler of connection to DB
    conn = None

    # Init of class TestCrud
    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))
        # Local Logger
        cls.logger = Logger('crud_logger', 'Logs/test_crud.log').logger
        # Ordering API mocker
        cls.oam = OrderingAPI_Mocker()
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
        # Json Data Order responses handler
        cls.jdata_orders_responses = JSONDataReader('DATA/ORDER_RESPONSE_DATA.json')
        # Docker manager
        cls.docker = DockerManager()
        # Timeout
        cls.timeout = 5

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

    # TC001
    def test_create_order(self, message_body=None):
        """
        TC_ID: TC001
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_create_order
        Description: By default function creates normal order,but can get any order to try creating
                     Function tests Ordering service creation order by RabbitMQ.
                     Function sends message to RabbitMQ queue Ordering to create order,
                     Ordering service have to create order in DB.
                     Validates if order is created and with status.
        """
        try:

            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            if message_body is None:
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
                        f'{self.test_create_order.__doc__}Order Id in DB -> Actual: ID {self.new_order_id} , '
                        f'Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(current_status, int(os.getenv('SUBMITTED')))
                    self.logger.info(
                        f'{self.test_create_order.__doc__} '
                        f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
        except Exception as e:
            self.logger.exception(f"\n{self.test_create_order.__doc__}{e}")
            raise

    # TC002
    def test_create_order_empty_list(self):
        """
        TC_ID: TC002
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_create_order_empty_list
        Description: 1.Function creates order with empty list of item,order must not to be created.
                     2.Function tests Ordering service creation order by RabbitMQ.
                     3.Function sends message to RabbitMQ queue Ordering to create order,
                     4.Validates if order is not created.
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message message_body to send
            message_body = self.jdata_orders.get_json_order('alice_order_empty_list', self.order_uuid)
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
                    self.logger.error(
                        f'{self.test_create_order_empty_list.__doc__}Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: Order not created')
                    raise Exception('Order with empty list created,this is wrong')
                # Timeout
                elif time.time() - start_time > self.timeout:
                    self.logger.info(
                        f'{self.test_create_order_empty_list.__doc__}Order in DB -> Actual: Order not created , '
                        f'Expected: Order not created')
                    break
        except Exception as e:
            self.logger.exception(f"\n{self.test_create_order_empty_list.__doc__}{e}")
            raise

    # TC003
    def test_create_order_0_quantity(self):
        """
        TC_ID: TC003
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_create_order_0_quantity
        Description: Function creates order with list of items in zero quantity,order may not to be created.
                     Function tests Ordering service creation order by RabbitMQ.
                     Function sends message to RabbitMQ queue Ordering to create order,
                     Ordering service have to create order in DB.
                     Validates if order is not created.
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message message_body to send
            message_body = self.jdata_orders.get_json_order('alice_order_0_quantity', self.order_uuid)
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
                    self.logger.error(
                        f'{self.test_create_order_0_quantity.__doc__}Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: Order not created')
                    raise Exception('Order with empty list created')
                # Timeout
                elif time.time() - start_time > self.timeout:
                    self.logger.info(
                        f'{self.test_create_order_0_quantity.__doc__}Order in DB -> Actual: Order not created , '
                        f'Expected: Order not created')
                    break
        except Exception as e:
            self.logger.exception(f"\n{self.test_create_order_0_quantity.__doc__}{e}")
            raise

    # TC004
    def test_cancel_order_v1(self):
        """
        TC_ID: TC004
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v1
        Description: Function tests Ordering api cancel request when order status is 1 (submitted).
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Cancels order in DB.
                     4. Validates order status is canceled in DB.
        """
        try:
            # Order creation
            self.test_create_order()
            # Cancel via mocker the order in status 1 (submitted)
            # Ordering api sends request to cancel order
            cancel_response = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Wait sec
            # Response validation must be 200
            self.assertEqual(cancel_response.status_code, 200)
            self.logger.info(
                f'{self.test_cancel_order_v1.__doc__}Response to cancel status -> '
                f'Actual:  {cancel_response.status_code} , Expected:{200}')

            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_order_status, int(os.getenv('CANCELLED')))
            self.logger.info(
                f"{self.test_cancel_order_v1.__doc__}Order Id {self.new_order_id} status in DB after cancel-> "
                f"Actual:  {current_order_status} ,Expected:{int(os.getenv('CANCELLED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v1.__doc__}{e}")
            raise

    # TC005
    def test_cancel_order_v2(self):
        """
        TC_ID: TC005
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v2
        Description: Function tests Ordering api cancel request when order status is 2 (awaitingvalidation).
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Updated order status in DB via SQL query.
                     4. Validates order status changed in DB.
                     5. Cancels order in DB.
                     6. Validates order status is canceled in DB.
        """
        try:
            # Order creation
            self.test_create_order()
            # Updating order status in DB to 2 (awaitingvalidation)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('AWAITINGVALIDATION')))
            # Validation status changed
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('AWAITINGVALIDATION')))
            self.logger.info(
                f"{self.test_cancel_order_v2.__doc__}Updating Order status in DB -> "
                f"Actual:  {current_status} ,Expected:{int(os.getenv('AWAITINGVALIDATION'))}")
            # Cancel via mocker the order in status 2 (awaitingvalidation)
            # Ordering api sends request to cancel order
            cancel_response = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 200
            self.assertEqual(cancel_response.status_code, 200)
            self.logger.info(
                f'{self.test_cancel_order_v2.__doc__}Response to cancel status -> '
                f'Actual:  {cancel_response.status_code} , Expected:{200}')
            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_order_status, int(os.getenv('CANCELLED')))
            self.logger.info(
                f"{self.test_cancel_order_v2.__doc__}Order Id {self.new_order_id} status in DB after cancel -> "
                f"Actual:  {current_order_status} ,Expected:{int(os.getenv('CANCELLED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v2.__doc__}{e}")
            raise

    # TC_006
    def test_cancel_order_v3(self):
        """
        TC_ID: TC006
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v3
        Description: Function tests Ordering api cancel request when order status is 3 (stockconfirmed).
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Updated order status in DB via SQL query.
                     4. Validates order status changed in DB.
                     5. Cancels order in DB.
                     6. Validates order status is canceled in DB.
        """
        try:
            # Order creation
            self.test_create_order()
            # Updating order status in DB to 3 (stockconfirmed)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('STOCKCONFIRMED')))
            # Validation status changed
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('STOCKCONFIRMED')))
            self.logger.info(
                f'{self.test_cancel_order_v3.__doc__}Updating Order status in DB ->'
                f"Actual:  {current_status} , Expected:{int(os.getenv('STOCKCONFIRMED'))}")
            # Cancel via mocker the order in status 3 (stockconfirmed)
            # Ordering api sends request to cancel order
            cancel_response = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 200
            self.assertEqual(cancel_response.status_code, 200)
            self.logger.info(
                f'{self.test_cancel_order_v3.__doc__}Request to cancel status -> '
                f'Actual:  {cancel_response.status_code} , Expected:{200}')
            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_order_status, int(os.getenv('CANCELLED')))
            self.logger.info(
                f"{self.test_cancel_order_v3.__doc__}Order status in DB after cancel-> "
                f"Actual:  {current_order_status} ,Expected:{int(os.getenv('CANCELLED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v3.__doc__}{e}")
            raise

    # TC007
    def test_cancel_order_v4(self):
        """
        TC_ID: TC007
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v4
        Description: Function tests Ordering api cancel request when order status is 4 (paid).
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Updated order status in DB via SQL query.
                     4. Validates order status changed in DB.
                     5. Cancels order in DB.
                     6. Validates order status is not canceled in DB.
        """
        try:
            # Clean messages from previous using of RabbitMQ queue
            with RabbitMQ() as mq:
                mq.purge('Ordering')
            # Order creation
            self.test_create_order()
            # Updating order status in DB to 4 (paid)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('PAID')))
            # Validation status changed
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('PAID')))
            self.logger.info(
                f'{self.test_cancel_order_v4.__doc__}Updating Order status in DB -> '
                f"Actual:  {current_status} , Expected:{int(os.getenv('PAID'))}")
            # Cancel via mocker the order in status 4 (paid)
            # Ordering api sends request to cancel order
            cancel_response = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 400
            self.assertEqual(cancel_response.status_code, 400)
            self.logger.info(
                f'{self.test_cancel_order_v4.__doc__}Request to cancel status -> '
                f'Actual:  {cancel_response.status_code} , Expected:{400}')
            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_order_status, int(os.getenv('PAID')))
            self.logger.info(
                f"{self.test_cancel_order_v4.__doc__}Order status in DB after cancel-> "
                f"Actual:  {current_order_status} , Expected:{int(os.getenv('PAID'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v4.__doc__}{e}")
            raise

    # TC008
    def test_cancel_order_v5(self):
        """
        TC_ID: TC008
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_cancel_order_v5
        Description: Function tests Ordering api cancel request when order status is 5 (shipped).
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Updated order status in DB via SQL query.
                     4. Validates order status changed in DB.
                     5. Cancels order in DB.
                     6. Validates order status is not canceled in DB.
        """
        try:
            # Order creation
            self.test_create_order()
            # Updating order status in DB to 5
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('SHIPPED')))
            # Validation status changed
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('SHIPPED')))
            self.logger.info(
                f"{self.test_cancel_order_v5.__doc__}Updating Order status in DB -> "
                f"Actual:  {current_status} , Expected:{int(os.getenv('SHIPPED'))}")
            # Cancel via mocker the order in status 1 (submitted)
            # Ordering api sends request to cancel order
            cancel_response = self.oam.cancel_order(self.new_order_id, self.order_uuid)
            # Response validation must be 400
            self.assertEqual(cancel_response.status_code, 400)
            self.logger.info(
                f'{self.test_cancel_order_v5.__doc__}Request to cancel status -> '
                f'Actual:  {cancel_response.status_code} , Expected:{400}')
            # Validation status canceled in DB
            # Get current status of the order
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_order_status, int(os.getenv('SHIPPED')))
            self.logger.info(
                f"{self.test_cancel_order_v5.__doc__}Order status in DB after cancel -> "
                f"Actual:  {current_order_status} , Expected:{int(os.getenv('SHIPPED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v5.__doc__}{e}")
            raise

    # TC009
    def test_get_order_details(self):
        """
        TC_ID: TC009
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_get_order_details
        Description: Function tests Ordering api get order.
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Validates response status 200.
                     4. Validates order details.
        """
        try:
            # Creating message_body message
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Order creation
            self.test_create_order(message_body)
            # Get order via Ordering API Mock
            order = self.oam.get_order_by_id(self.new_order_id)
            # Validating response status code
            self.assertEqual(order.status_code, 200)
            self.logger.info(
                f'{self.test_get_order_details.__doc__}Response to cancel status -> '
                f'Actual:  {order.status_code} , Expected:{200}')
            # Validating order details
            # Getting response body after mocking Ordering API
            response_body = order.json()
            # Zeroing date cause it automatically set by server time even date was existing
            response_body['date'] = 0
            # Loading stub response for that order
            response_stub = self.jdata_orders_responses.get_json_order_response('alice_normal_order_response',
                                                                                self.new_order_id)
            self.assertEqual(response_body, response_stub)
            self.logger.info(
                f'{self.test_get_order_details.__doc__}Response bodies -> '
                f'\nActual:  {response_body} ,\nExpected:{response_stub}')
        except Exception as e:
            self.logger.exception(f"\n{self.test_get_order_details.__doc__}{e}")
            raise

    # TC010
    def test_ship_order(self):
        """
        TC_ID: TC010
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_ship_order
        Description: Function tests Ordering api sends request to ship order.
                     1. Sends message to RabbitMQ queue to create order.
                     2. Validates order creation in DB with status 1.
                     3. Updates status to 4(paid).
                     4. Cancels order in DB.
                     5. Validates response status 400.
        """
        try:
            # Order creation
            self.test_create_order()
            # Updating status to 4 (paid) via sql query
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('PAID')))
            # Getting amd checking order status
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('PAID')))
            # Logging
            self.logger.info(
                f"{self.test_ship_order.__doc__}Order status in DB -> "
                f"Actual:  {current_status} , Expected: {int(os.getenv('PAID'))}")
            # Ordering api sends request to ship order
            cancel_response = self.oam.ship_order(self.new_order_id, self.order_uuid)
            # Response validation must be 200
            self.assertEqual(cancel_response.status_code, 200)
            self.logger.info(
                f'{self.test_ship_order.__doc__}Response to ship order -> '
                f'Actual:  {cancel_response.status_code} , Expected:{200}')
            # Validate order status 5 (shipped) in DB
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(current_status, int(os.getenv('SHIPPED')))
            self.logger.info(
                f"{self.test_ship_order.__doc__}Order status in DB -> "
                f"Actual:  {current_status} , Expected: {int(os.getenv('SHIPPED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_ship_order.__doc__}{e}")
