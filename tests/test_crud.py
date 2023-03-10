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
        Date:
        Function Name: test_create_order
        Description:
        """
        pass
        try:
            x = create_order(self.order_uuid)
            y = self.conn.select_query('select TOP 1 o.Id from ordering.orders as o where BuyerId = 11 and '
                                       'o.OrderStatusId'
                                       '= 1 order by Id desc')
            self.assertTrue(len(y), 1)
            self.logger.info(f'{self.test_ship_order.__doc__}Actual: {y} , Expected: Order Id in DB ')
        except Exception as e:
            self.logger.exception(f"\n{self.test_ship_order.__doc__}{e}")
            raise

    def test_cancel_order_v1(self):
        """
        Name: Artsyom Sharametsieu
        Date:
        Function Name: test_cancel_order_v1
        Description:
        """
        pass
        try:
            x = self.conn.select_query('select TOP 1 o.Id from ordering.orders as o where BuyerId = 11 and '
                                       'o.OrderStatusId'
                                       '= 1 order by Id desc')
            order_id_db = x[0]['Id']
            y = self.oam.cancel_order(order_id_db, self.order_uuid)
            self.assertTrue(y, 200)
            self.logger.info(f'{self.test_cancel_order_v1.__doc__}Actual: {y} , Expected:{200} ')
        except Exception as e:
            self.logger.exception(f"\n{self.test_cancel_order_v1.__doc__}{e}")
            raise
