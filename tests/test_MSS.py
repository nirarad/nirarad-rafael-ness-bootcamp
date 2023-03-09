from time import sleep

import pytest
from dotenv import load_dotenv
import os
import threading

from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.eshop_rabbitmq_events import create_order, confirm_stock, payment_succeeded, reject_stock
from utils.rabbitmq.rabbitmq_receive import callback
from utils.rabbitmq.rabbitmq_send import RabbitMQ


@pytest.fixture
def MSS_scenario():
     try:
        load_dotenv('test.env')
        api = OrderingAPI()
        return api
     except Exception:
         print("api instance faield")

def test_mss(MSS_scenario):
    try:
        create_order(100)
        OrderID=0
        sleep(5)
        with MSSQLConnector() as conn:
            res=conn.select_query(os.getenv('STATUS_1_2_QUERY'))
            if len(res) != 0:
                OrderID=res[0]['Id']
                print(OrderID)
            else:
                print("result is empty")
                #exit(1)
        sleep(5)
        confirm_stock(OrderID)
        sleep(5)
        payment_succeeded(OrderID)
        sleep(5)
        with MSSQLConnector() as conn:
            res = conn.select_query(
                f'select [ordering].[orders].OrderStatusId from [ordering].[orders] where [ordering].[orders].Id={OrderID}')
            assert res[0]['OrderStatusId'] == 4
            print("sucsses")
    except Exception:
        print('test faiel')


def test_stock_reject(MSS_scenario):
    try:
        mq=RabbitMQ()
        thread = threading.Thread(target=mq.consume('Ordering', callback), args=(callback))
        thread.start()
        create_order(100)
        OrderID=0
        sleep(5)
        with MSSQLConnector() as conn:
            res=conn.select_query('SELECT ordering.orders.Id from ordering.orders where ordering.orders.OrderStatusId in (1,2)')
            if len(res) != 0:
                OrderID=res[0]['Id']
                print(OrderID)
            else:
                print("result is empty")
        sleep(10)
        reject_stock(OrderID)
        api=OrderingAPI()
        res=api.cancel_order(OrderID)
        assert res.reason == int(os.getenv('200'))
        print('Pass')
    except Exception:
        print("test faield")











