import threading
import time
import unittest

from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.eshop_rabbitmq_events import *
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger
from simulators.payment_simulator import PaymentSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.basket_simulator import BasketSimulator
from dotenv import load_dotenv


class FunctionalSuit(unittest.TestCase):
    # Tests of functionality of ordering api with payment,basket,catalog simulators

    # Handler of connection to DB
    catalog_sim = None
    payment_sim = None
    docker = None
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))
        # Docker manager
        cls.docker = DockerManager()
        # Local Logger
        cls.logger = Logger('functional_logger', 'Logs/test_functional.log').logger
        # Unique id generator
        cls.order_uuid = str(uuid.uuid4())
        # Connection to DB
        cls.conn = MSSQLConnector()
        # Order Id saver
        cls.new_order_id = None
        # Json Data Order handler
        cls.jdata_orders = JSONDataReader('DATA/ORDERS_DATA.json')
        # Json Data Order responses handler
        cls.jdata_orders_responses = JSONDataReader('DATA/ORDER_RESPONSE_DATA.json')
        # Payment simulator
        cls.payment_sim = PaymentSimulator(time_limit=50)
        # Catalog simulator
        cls.catalog_sim = CatalogSimulator(time_limit=50)
        # Success payment thread
        cls.consume_to_succeed_payment_thread = threading.Thread(target=cls.payment_sim.consume_to_succeed_payment)
        # Failed payment thread
        cls.consume_to_fail_payment_thread = threading.Thread(target=cls.payment_sim.consume_to_fail_payment)
        # Catalog thread for items in stock
        cls.consume_to_confirm_stock_thread = threading.Thread(target=cls.catalog_sim.consume_to_confirm_stock)
        # Catalog thread for items not in stock
        cls.consume_to_reject_stock_thread = threading.Thread(target=cls.catalog_sim.consume_to_reject_stock)
        # Basket simulator
        cls.basket_sim = BasketSimulator()
        # Last order created
        cls.last_order = None
        # Timeout
        cls.timeout = 120
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()

    def setUp(self) -> None:
        # Run common containers and stop not needed or crashed
        self.docker.stop(os.getenv('ORDERING_BACKGROUNDTASKS_CONTAINER'))
        self.docker.start(os.getenv('RABBITMQ_CONTAINER'))
        self.docker.start(os.getenv('SQLDATA_CONTAINER'))
        self.docker.start(os.getenv('ORDERING_CONTAINER'))
        self.docker.start(os.getenv('IDENTITY_CONTAINER'))
        # Clean messages from previous using of RabbitMQ queues
        with RabbitMQ() as mq:
            mq.purge_all()
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # PAYMENT
    # TC011
    def test_order_payment_succeeded(self):
        """
        TC_ID: TC011
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_payment_succeeded
        Description: 1.Function tests functionality of positive payment by Ordering api and Payment simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to stockconfirmed.
                     5.Validates the status.
                     6.Sends message to Payment queue.
                     7.Sends message to Ordering queue.
                     8.Validates order status in DB changed to (paid).
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = self.basket_sim.create_order(message_body)
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
                        f'{self.test_order_payment_succeeded.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f"{self.test_order_payment_succeeded.__doc__} "
                        f"Order status in DB -> Actual: {current_status} , "
                        f"Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Updating order status in DB to 3 (stockconfirmed)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('STOCKCONFIRMED')))
            # Validating order status in DB
            self.assertEqual(int(os.getenv('STOCKCONFIRMED')), self.conn.get_order_status_from_db(self.new_order_id))
            self.logger.info(
                f"{self.test_order_payment_succeeded.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, "
                f"Expected: {int(os.getenv('STOCKCONFIRMED'))}")
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Sending message to Payment queue that order confirmed in stock
            status_changed_to_stock(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Payment simulator confirms payment succeeded
            self.consume_to_succeed_payment_thread.start()
            # Getting current order status
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            # Wait until ordering api updating order status
            start_time = time.time()
            while current_status != int(os.getenv('PAID')):
                current_status = self.conn.get_order_status_from_db(self.new_order_id)
                # Timeout
                if time.time() - start_time > self.timeout:
                    raise Exception("Order status is not updated")
            # Stopping simulator
            self.payment_sim.stop = True
            # Validating status 4 (paid) in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(int(os.getenv('PAID')), order_status)
            self.logger.info(
                f"{self.test_order_payment_succeeded.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {int(os.getenv('PAID'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_payment_succeeded.__doc__}{e}")
            raise

    # TC012
    def test_order_payment_failed(self):
        """
        TC_ID: TC012
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_payment_failed
        Description: 1.Function tests functionality of negative payment by Ordering api and Payment simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to 3 (stockconfirmed).
                     5.Validates the status.
                     6.Sends message to Payment queue.
                     7.Sends message to Ordering queue.
                     8.Validates order status in DB changed to 6 (cancelled).
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = self.basket_sim.create_order(message_body)
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
                        f'{self.test_order_payment_failed.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f"{self.test_order_payment_failed.__doc__} "
                        f"Order status in DB -> Actual: {current_status} , "
                        f"Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Updating order status in DB to 3 (stockconfirmed)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('STOCKCONFIRMED')))
            # Validating order status in DB
            self.assertEqual(int(os.getenv('STOCKCONFIRMED')), self.conn.get_order_status_from_db(self.new_order_id))
            self.logger.info(
                f"{self.test_order_payment_failed.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)},"
                f"Expected: {int(os.getenv('STOCKCONFIRMED'))}")
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Sending message to Payment queue that order confirmed in stock
            status_changed_to_stock(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Payment simulator fails payment
            self.consume_to_fail_payment_thread.start()
            # Getting current order status
            current_status = self.conn.get_order_status_from_db(self.new_order_id)
            # Wait until status will update
            start_time = time.time()
            while current_status != int(os.getenv('CANCELLED')):
                current_status = self.conn.get_order_status_from_db(self.new_order_id)
                # Timeout
                if time.time() - start_time > self.timeout:
                    raise Exception("Order status is not updated")
            # Stopping payment simulator
            self.payment_sim.stop = True
            # Validating status 6 (cancelled) in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(int(os.getenv('CANCELLED')), order_status)
            self.logger.info(
                f"{self.test_order_payment_failed.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)},"
                f"Expected: {int(os.getenv('CANCELLED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_payment_failed.__doc__}{e}")
            raise

    # CATALOG
    # TC013
    def test_order_in_stock(self):
        """
        TC_ID: TC013
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_in_stock
        Description: 1.Function tests functionality of positive stock confirmation
                     by Ordering api and Catalog simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to 2 (awaitingvalidation).
                     5.Validates the status.
                     6.Sends message to Catalog queue.
                     7.Invokes Catalog simulator to send message to Ordering queue.
                     8.Validates order status in DB changed to 3 (stockconfirmed).
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = self.basket_sim.create_order(message_body)
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
                        f'{self.test_order_in_stock.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f'{self.test_order_in_stock.__doc__} '
                        f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Status was not updated")
            # Updating order status in DB to 2 (awaitingvalidation)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('AWAITINGVALIDATION')))
            # Validating order status in DB
            self.assertEqual(int(os.getenv('AWAITINGVALIDATION')),
                             self.conn.get_order_status_from_db(self.new_order_id))
            self.logger.info(
                f"{self.test_order_in_stock.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, "
                f"Expected: {int(os.getenv('AWAITINGVALIDATION'))}")
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Sending message to Catalog queue that order confirmed in stock
            status_changed_to_awaitingvalidation(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Catalog simulator confirms payment succeeded
            self.consume_to_confirm_stock_thread.start()
            # Wait until status will update
            start_time = time.time()
            while current_status != int(os.getenv('STOCKCONFIRMED')):
                current_status = self.conn.get_order_status_from_db(self.new_order_id)
                # Timeout
                if time.time() - start_time > self.timeout:
                    raise Exception("Order status is not updated")
            # Stopping Catalog simulator
            self.catalog_sim.stop = True
            # Validating status paid in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(int(os.getenv('STOCKCONFIRMED')), order_status)
            self.logger.info(
                f"{self.test_order_in_stock.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, "
                f"Expected: {int(os.getenv('STOCKCONFIRMED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_in_stock.__doc__}{e}")
            raise

    # TC014
    def test_order_not_in_stock(self):
        """
        TC_ID: TC014
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_not_in_stock
        Description: 1.Function tests functionality of negative stock confirmation
                     by Ordering api and Catalog simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to awaitingvalidation.
                     5.Validates the status.
                     6.Sends message to Catalog queue.
                     7.Invokes Catalog simulator to send message to Ordering queue.
                     8.Validates order status in DB changed to cancel.
        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = self.basket_sim.create_order(message_body)
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
                        f'{self.test_order_not_in_stock.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id},Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f"{self.test_order_not_in_stock.__doc__} "
                        f"Order status in DB -> Actual: {current_status} , Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Updating order status in DB to 2 (awaitingvalidation)
            self.conn.update_order_db_status(self.new_order_id, int(os.getenv('AWAITINGVALIDATION')))
            # Validating order status in DB
            self.assertEqual(int(os.getenv('AWAITINGVALIDATION')),
                             self.conn.get_order_status_from_db(self.new_order_id))
            self.logger.info(
                f"{self.test_order_not_in_stock.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, "
                f"Expected: {int(os.getenv('AWAITINGVALIDATION'))}")
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Sending message to Catalog queue that order confirmed in stock
            status_changed_to_awaitingvalidation(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Catalog simulator rejecting stock
            self.consume_to_reject_stock_thread.start()
            # Wait until status will update
            start_time = time.time()
            while current_status != int(os.getenv('CANCELLED')):
                current_status = self.conn.get_order_status_from_db(self.new_order_id)
                # Timeout
                if time.time() - start_time > self.timeout:
                    raise Exception("Order status is not updated")
            # Stopping Catalog simulator
            self.catalog_sim.stop = True
            # Validating status 6 (cancelled) in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            self.assertEqual(int(os.getenv('CANCELLED')), order_status)
            self.logger.info(
                f"{self.test_order_not_in_stock.__doc__}Order status in DB -> "
                f"Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, "
                f"Expected: {int(os.getenv('CANCELLED'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_order_not_in_stock.__doc__}{e}")
            raise

    # BackgroundTasks api
    # TC015
    def test_backgroundtasks_searching_new_order(self):
        """
        TC_ID: TC015
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_backgroundtasks_searching_new_order
        Description: 1.Function tests Ordering BackgroundTasks functionality.
                     2.Function creating order,Order creates by Ordering api.
                     3.Validates if order is created and with status 1.
                     5.Validates the status 2.Ordering.backgroundtasks searching new order,when the order found,sends to
                     Ordering api to update status 2 (awaitingvalidation).
        """
        try:
            self.docker.start(os.getenv('ORDERING_BACKGROUNDTASKS_CONTAINER'))
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            order = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            self.basket_sim.create_order(order)
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
                        f'{self.test_backgroundtasks_searching_new_order.__doc__}Order Id in DB -> '
                        f'Actual: ID {self.new_order_id} , Expected: New Order Id')
                    # Validate status order is 1 (submitted)
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertEqual(int(os.getenv('SUBMITTED')), current_status)
                    self.logger.info(
                        f"{self.test_backgroundtasks_searching_new_order.__doc__} "
                        f"Order status in DB -> Actual: {current_status} , "
                        f"Expected: {int(os.getenv('SUBMITTED'))}")
                    break
                # Timeout
                elif time.time() - start_time > self.timeout:
                    raise Exception("Record was not created")
            # Wait until status will update
            start_time = time.time()
            while current_status != int(os.getenv('AWAITINGVALIDATION')):
                current_status = self.conn.get_order_status_from_db(self.new_order_id)
                # Timeout
                if time.time() - start_time > self.timeout:
                    raise Exception("Order status is not updated")
            # Assert to status 2 (awaitingvalidation)
            self.assertEqual(int(os.getenv('AWAITINGVALIDATION')), current_status)
            self.logger.info(
                f"{self.test_backgroundtasks_searching_new_order.__doc__}Order status ID in DB -> "
                f"Actual: {current_status}, Expected: {int(os.getenv('AWAITINGVALIDATION'))}")
        except Exception as e:
            self.logger.exception(f"\n{self.test_backgroundtasks_searching_new_order.__doc__}{e}")
            raise


if __name__ == '__main__':
    unittest.main()
