from pprint import pprint

import pytest
import requests

from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.simulators.basket import Basket


class TestSanity(object):
    @pytest.fixture
    def setup(self):
        rbtMQ = RabbitMQ()
        self.basket = Basket(rbtMQ)
        return OrderingAPI()

    def test_api(self,setup):
        res = OrderingAPI.get_order_by_id(1)
        # res = requests.get('http://localhost:5102/api/v1/orders')
        pprint(res)