import time
import unittest

from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import *
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger
from simulators.payment_simulator import PaymentSimulator
from simulators.catalog_simulator import CatalogSimulator
from simulators.basket_simulator import BasketSimulator


class TestIntegration(unittest.TestCase):
    # Tests of integration with payment,basket,catalog simulators

    # Variable of connection to DB
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Env of tests
        load_dotenv('DATA/.env.test')

        # Local Logger
        cls.logger = Logger('integration_logger', 'Logs/test_integration.log').logger

        # Unique id generator
        cls.order_uuid = str(uuid.uuid4())

        # Connection to DB
        cls.conn = MSSQLConnector()

        # Order Id saver
        cls.new_order_id = None

        # Json Data Order handler
        cls.jdata_orders = JSONDataReader(os.getenv('ORDERS_PATH'))

        # Json Data Order responses handler
        cls.jdata_orders_responses = JSONDataReader(os.getenv('RESPONSES_PATH'))

        # Payment simulator
        cls.payment_sim = PaymentSimulator()

        # Catalog simulator
        cls.catalog_sim = CatalogSimulator()

        # Basket simulator
        cls.basket_sim = BasketSimulator()

        # Last order created
        cls.last_order = None

        # Timeout
        cls.timeout = 40

    def setUp(self) -> None:
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # PAYMENT
    # TC011
    def test_integration_with_payment_succeeded(self):
        """
        TC_ID: TC011
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_integration_with_payment_succeeded
        Description: 1.Function tests Ordering service integration with Payment simulator.
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
            body_after_sending = create_order(message_body)
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
                        f'{self.test_integration_with_payment_succeeded.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_integration_with_payment_succeeded.__doc__} '
                        f'Order status in DB -> Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)

            # Updating order status in DB to stockconfirmed
            self.conn.update_order_db_status(self.new_order_id, 3)
            # Validating order status in DB
            self.assertEqual(self.conn.get_order_status_from_db(self.new_order_id), 3)
            self.logger.info(
                f'{self.test_integration_with_payment_succeeded.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {3}')
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Getting date created automatically by server in code
            # Sending message to Payment queue that order confirmed in stock
            status_changed_to_stock(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Payment simulator confirms payment succeeded
            self.payment_sim.succeed_pay()

            # Wait for ordering service updating order status
            time.sleep(self.timeout)
            # Validating status paid in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            # WAIT UPDATING ORDER STATUS IN DB
            time.sleep(5)
            self.assertEqual(order_status, 4)
            self.logger.info(
                f'{self.test_integration_with_payment_succeeded.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {4}')

        except Exception as e:
            self.logger.exception(f"\n{self.test_integration_with_payment_succeeded.__doc__}Actual {e}")
            raise

    # TC012
    def test_integration_with_payment_failed(self):
        """
        TC_ID: TC012
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_integration_with_payment_failed
        Description: 1.Function tests Ordering service integration with Payment simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to stockconfirmed.
                     5.Validates the status.
                     6.Sends message to Payment queue.
                     7.Sends message to Ordering queue.
                     8.Validates order status in DB changed to (cancelled).

        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = create_order(message_body)
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
                        f'{self.test_integration_with_payment_failed.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_integration_with_payment_failed.__doc__} '
                        f'Order status in DB -> Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)

            # Updating order status in DB to stockconfirmed
            self.conn.update_order_db_status(self.new_order_id, 3)
            # Validating order status in DB
            self.assertEqual(self.conn.get_order_status_from_db(self.new_order_id), 3)
            self.logger.info(
                f'{self.test_integration_with_payment_failed.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {3}')
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Getting date created automatically by server in code
            # Sending message to Payment queue that order confirmed in stock
            status_changed_to_stock(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Payment simulator confirms payment succeeded
            self.payment_sim.failed_pay()

            # Wait for ordering service updating order status
            time.sleep(self.timeout)
            # Validating status paid in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            # WAIT UPDATING ORDER STATUS IN DB
            time.sleep(5)
            self.assertEqual(order_status, 6)
            self.logger.info(
                f'{self.test_integration_with_payment_failed.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {6}')

        except Exception as e:
            self.logger.exception(f"\n{self.test_integration_with_payment_failed.__doc__}Actual {e}")
            raise

    # CATALOG
    # TC013
    def test_integration_with_catalog_in_stock(self):
        """
        TC_ID: TC013
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_integration_with_catalog_in_stock
        Description: 1.Function tests Ordering service integration with Catalog simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to awaitingvalidation.
                     5.Validates the status.
                     6.Sends message to Catalog queue.
                     7.Invokes Catalog simulator to send message to Ordering queue.
                     8.Validates order status in DB changed to (stockconfirmed).

        """
        try:
            # Find last order id to compare if getting right order id,will be pre last after creating new order
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            # Message body to send
            message_body = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            # Sending message to RabbitMQ to Ordering queue to create order and getting body corrected by server
            body_after_sending = create_order(message_body)
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
                        f'{self.test_integration_with_catalog_in_stock.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id}, Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_integration_with_catalog_in_stock.__doc__}'
                        f' Order status in DB -> Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)

            # Updating order status in DB to stockconfirmed
            self.conn.update_order_db_status(self.new_order_id, 2)
            # Validating order status in DB
            self.assertEqual(self.conn.get_order_status_from_db(self.new_order_id), 2)
            self.logger.info(
                f'{self.test_integration_with_catalog_in_stock.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {2}')
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)

            # Getting date created automatically by server in code
            # Sending message to Catalog queue that order confirmed in stock
            status_changed_to_awaitingvalidation(self.new_order_id, self.order_uuid, sent_body['CreationDate'])
            # Catalog simulator confirms payment succeeded
            self.catalog_sim.confirm_stock()

            # Wait for ordering api updating order status
            time.sleep(self.timeout)
            # Validating status paid in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            # WAIT UPDATING ORDER STATUS IN DB
            time.sleep(5)
            self.assertEqual(order_status, 3)
            self.logger.info(
                f'{self.test_integration_with_catalog_in_stock.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {3}')

        except Exception as e:
            self.logger.exception(f"\n{self.test_integration_with_catalog_in_stock.__doc__}Actual {e}")
            raise

    # TC014
    def test_integration_with_catalog_not_in_stock(self):
        """
        TC_ID: TC014
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_not_in_stock_
        Description: 1.Function tests Ordering service integration with Catalog simulator.
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
            body_after_sending = create_order(message_body)
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
                        f'{self.test_integration_with_catalog_not_in_stock.__doc__}'
                        f'Order Id in DB -> Actual: ID {self.new_order_id},Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_integration_with_catalog_not_in_stock.__doc__} '
                        f'Order status in DB -> Actual: {current_status} ,Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
                # Updating timer
                time.sleep(0.1)

            # Updating order status in DB to stockconfirmed
            self.conn.update_order_db_status(self.new_order_id, 2)
            # Validating order status in DB
            self.assertEqual(self.conn.get_order_status_from_db(self.new_order_id), 2)
            self.logger.info(
                f'{self.test_integration_with_catalog_not_in_stock.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {2}')
            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)

            # Getting date created automatically by server in code
            # Sending message to Catalog queue that order confirmed in stock
            status_changed_to_awaitingvalidation(self.new_order_id, self.order_uuid, sent_body['CreationDate'])

            # Catalog simulator confirms payment succeeded
            self.catalog_sim.reject_stock()

            # Wait for ordering service updating order status
            time.sleep(self.timeout)
            # Validating status paid in order in DB
            order_status = self.conn.get_order_status_from_db(self.new_order_id)
            # WAIT UPDATING ORDER STATUS IN DB
            time.sleep(5)
            self.assertEqual(order_status, 6)
            self.logger.info(
                f'{self.test_integration_with_catalog_not_in_stock.__doc__}Order status in DB -> '
                f'Actual: {self.conn.get_order_status_from_db(self.new_order_id)}, Expected: {6}')

        except Exception as e:
            self.logger.exception(f"\n{self.test_integration_with_catalog_not_in_stock.__doc__}Actual {e}")
            raise

    # BASKET
    # TC015
    def test_order_api_integration_with_basket(self):
        """
        TC_ID: TC015
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_not_in_stock_
        Description: 1.Function tests Ordering service integration whit Catalog simulator.
                     2.Function creating order.
                     3.Validates if order is created and with status.
                     4.Changes status to awaitingvalidation.
                     5.Validates the status.
                     6.Sends message to Catalog queue.
                     7.Invokes Catalog simulator to send message to Ordering queue.
                     8.Validates order status in DB changed to cancel.

        """
        try:
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            order = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            self.basket_sim.place_order(order)
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
                        f'{self.test_order_api_integration_with_basket.__doc__}Order Id in DB -> '
                        f'Actual: ID {self.new_order_id} , Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_order_api_integration_with_basket.__doc__} Order status in DB ->'
                        f' Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")

                # Basket consuming for message from Ordering api
                self.basket_sim.consume()
                # If message didn't come than something broken in Ordering api
                self.assertNotEqual(self.basket_sim.response_message, None)
            self.logger.info(
                f'{self.test_order_api_integration_with_basket.__doc__}Message fro Ordering API -> '
                f'Actual: {self.basket_sim.response_message}, Expected: not None')

        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_integration_with_basket.__doc__}Actual {e}")
            raise

    # BackgroundTasks service
    # TC016
    def test_order_api_integration_with_backgroundtasks(self):
        """
        TC_ID: TC016
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_order_api_integration_with_backgroundtasks
        Description: 1.Function tests Ordering service integration whit Ordering BackgroundTasks service.
                     2.Function creating order.
                     3.Validates if order is created and with status 1.
                     5.Validates the status 2.
        """
        try:
            last_order_record_in_db = self.conn.get_last_order_record_id_in_db()
            order = self.jdata_orders.get_json_order('alice_normal_order', self.order_uuid)
            self.basket_sim.place_order(order)
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
                        f'{self.test_order_api_integration_with_backgroundtasks.__doc__}Order Id in DB -> '
                        f'Actual: ID {self.new_order_id} , Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_order_api_integration_with_backgroundtasks.__doc__} Order status in DB ->'
                        f' Actual: {current_status} , Expected: {1}')
                    break
                # if 10 sec pass no sense to wait
                elif time.time() - start_time > 10:  # Timeout after 10 seconds
                    raise Exception("Record was not created")
            # Wait for BackgroundTasks sending message to Ordering api and ordering api updates order status to 2.
            time.sleep(self.timeout)
            current_order_status = self.conn.get_order_status_from_db(self.new_order_id)
            # Assert to status 2 (awaitingvalidation)
            self.assertEqual(current_order_status, 2)
            self.logger.info(
                f'{self.test_order_api_integration_with_backgroundtasks.__doc__}Order status ID in DB -> '
                f'Actual: {current_order_status}, Expected: {2}')

        except Exception as e:
            self.logger.exception(f"\n{self.test_order_api_integration_with_backgroundtasks.__doc__}Actual {e}")
            raise


if __name__ == '__main__':
    unittest.main()
