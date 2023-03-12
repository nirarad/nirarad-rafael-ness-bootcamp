import pytest
from utils import *
import pyodbc
import json
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages
from utils.rabbitmq.rabbitmq_send import RabbitMQ
#from utils.api.ordering_api import BearerTokenizer
from utils.api.ordering_api import OrderingAPI
from utils.api.bearer_tokenizer import BearerTokenizer
from utils.rabbitmq.rabbitmq_receive import *
from time import sleep

# @pytest.fixture
# def sql():
#     return MSSQLConnector()
@pytest.fixture()
def messages():
    return RabbitMessages()

@pytest.fixture()
def order_api():
    return OrderingAPI()

@pytest.fixture()
def rabbitsend():
    return RabbitMQ()

@pytest.mark.test_MSS
def test_MSS(messages,rabbitsend):
    productid=1
    quantity=1
    body = messages.usercheckout(productid,quantity)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                ordersnum=conn.select_query('SELECT COUNT(Id) from ordering.orders')

                mq.publish(exchange='eshop_event_bus',routing_key='UserCheckoutAcceptedIntegrationEvent',body=json.dumps(body))

                mq.consume('Basket', callback)
                assert returnglob() == 'OrderStartedIntegrationEvent'

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'

                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 1

                mq.consume('Catalog', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 2

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

                body=messages.stockconfirmed()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

                mq.consume('Payment', callback)
                assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 3

                body = messages.paymentsuccses()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentSucceededIntegrationEvent', body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToPaidIntegrationEvent'

                mq.consume('Catalog', callback)
                assert returnglob() == 'OrderStatusChangedToPaidIntegrationEvent'

                result=conn.select_query('SELECT COUNT(Id) from ordering.orders')
                orderstatus=conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
    assert result[0]['']==ordersnum[0]['']+1
    assert orderstatus[0]['OrderStatusId']==4


@pytest.mark.test_outofstock
def test_outofstock(messages):
    productid = 1
    quantity = 10000
    body = messages.usercheckout(productid, quantity)

    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))
            mq.consume('Basket', callback)
            assert returnglob() == 'OrderStartedIntegrationEvent'

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'

            mq.consume('Catalog', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

            body=messages.stockreject()
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockRejectedIntegrationEvent',
                       body=json.dumps(body))
    sleep(15)
    with MSSQLConnector() as conn:
            result = conn.select_query('SELECT COUNT(Id) from ordering.orders')
            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
    assert result[0][''] == ordersnum[0][''] + 1
    assert orderstatus[0]['OrderStatusId'] == 6


@pytest.mark.test_paymentfail
def test_paymentfail(messages):
    productid = 1
    quantity = 1
    body = messages.usercheckout(productid, quantity)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            mq.consume('Basket', callback)
            assert returnglob() == 'OrderStartedIntegrationEvent'
            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 1

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'

            mq.consume('Catalog', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
            orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 2

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'


            body = messages.stockconfirmed()
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(body))

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

            mq.consume('Payment', callback)
            assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 3

            body = messages.paymentfail()
            mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentFailedIntegrationEvent',
                       body=json.dumps(body))

            sleep(8)
            result = conn.select_query('SELECT COUNT(Id) from ordering.orders')
            orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
    assert result[0][''] == ordersnum[0][''] + 1
    assert orderstatus[0]['OrderStatusId'] == 6



@pytest.mark.test_update_order_to_shiped
def test_update_order_to_shiped(order_api):
        with MSSQLConnector() as conn:
            orderid=conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
            orderid=orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
        assert newstatus[0]['OrderStatusId']==5

@pytest.mark.test_cancel_order_status_2
def test_cancel_order_status_2(order_api):
    with MSSQLConnector() as conn:
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 2')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 6


@pytest.mark.test_cancel_order_status_3
def test_cancel_order_status_3(order_api):
    with MSSQLConnector() as conn:
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 3')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 6

@pytest.mark.test_cancel_order_status_4_fail
def test_cancel_order_status_4_fail(order_api):
    with MSSQLConnector() as conn:
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 4

@pytest.mark.test_cancel_order_status_5_fail
def test_cancel_order_status_5_fail(order_api):
    with MSSQLConnector() as conn:
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 5')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 5


# def test_update_order_to_shiped_fail(order_api):
#     with MSSQLConnector() as conn:
#         orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 3')
#         orderid = orderid[0]['']
#         order_api.update_to_shiped(orderid)
#         newstatus = conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
#         assert newstatus[0]['OrderStatusId'] == 5


