import unittest
from dotenv import load_dotenv

from utils.testcase.logger import Logger
from utils.api.ordering_api_mocker import OrderingAPI_Mocker


class TestAP(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv('.env.test')
        cls.logger = Logger('test', 'Logs/tests.log').logger
        cls.oam = OrderingAPI_Mocker()

    def setUp(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_ship_order(self):
        """
        Name: Artsyom Sharametsieu
        Date:
        Function Name:test_ship_order
        Description:
        """
        pass
        try:
            x = self.oam.ship_order(2, 'e05ebc63-8e5d-4530-b2ca-15e121fcc5d3')
            self.assertTrue(x, 200)
            self.logger.info(f'\n{self.test_ship_order.__doc__} Actual: {x} , Expected:{200} ')
        except Exception as e:
            self.logger.exception(f"\n{self.test_ship_order.__doc__}{e}")
            raise
