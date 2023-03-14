import os
import time
import unittest
import uuid

from dotenv import load_dotenv

from utils.api.ordering_api_mocker import OrderingAPI_Mocker
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import *
from utils.testcase.jsondatareader import JSONDataReader
from utils.testcase.logger import Logger
from simulators.payment_simulator import PaymentSimulator

class TestINTEGRATION(unittest.TestCase):
    # Tests of integration with payment,basket,catalog simulators

    # Variable of connection to DB
    conn = None

    @classmethod
    def setUpClass(cls) -> None:
        # Init of class TestCRUD

        # Env of tests
        load_dotenv('DATA/.env.test')

        # Local Logger
        cls.logger = Logger('test', 'Logs/tests.log').logger

        # Ordering API mocker
        cls.oam = OrderingAPI_Mocker()

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

    def setUp(self) -> None:
        self.conn.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # TC011
    def test_order_payment_succeeded(self):
        """
        TC_ID: TC011
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: test_create_order
        Description: By default function creates normal order.
                     Function tests Ordering service creation order by RabbitMQ.
                     Function sends message to RabbitMQ queue Ordering to create order,
                     Ordering service have to create order in DB.
                     Validates if order is created and with status.
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
                        f'{self.test_order_payment_succeeded.__doc__}Order Id in DB -> Actual: ID {self.new_order_id}, '
                        f'Expected: New Order Id')
                    # Validate status order is 1
                    current_status = self.conn.get_order_status_from_db(self.new_order_id)
                    self.assertTrue(current_status, 1)
                    self.logger.info(
                        f'{self.test_order_payment_succeeded.__doc__} Order status in DB -> Actual: {current_status} ,'
                        f' Expected: {1}')
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

            # Return back format of body from str to dict to get creation date
            sent_body = eval(body_after_sending)
            # Getting date created automatically by server in code

            # Payment simulator sends message to Ordering queue that payment succeeded
            payment_succeeded(self.new_order_id, self.order_uuid, sent_body['CreationDate'])

        except Exception as e:
            self.logger.exception(f"\n{self.test_order_payment_succeeded.__doc__}Actual {e}")
            raise


if __name__ == '__main__':
    unittest.main()
