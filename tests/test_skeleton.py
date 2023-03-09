import unittest
from dotenv import load_dotenv

from utils.api.ordering_api_mocker import OrderingAPI_Mocker
from utils.testcase.logger import Logger


class TestAP(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv('.env.test')
        cls.logger = Logger('test', 'tests').logger
        cls.ordering = OrderingAPI_Mocker()

    def setUp(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_tc(self):
        """
        Name: Artsyom Sharametsieu
        Date:
        Function Name:
        Description:
        """
        try:
            pass
        except Exception as e:
            self.logger.exception(f"{self.test_tc.__doc__}{e}")
            raise
