import pytest
from utils import *
import pyodbc
import json
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *
from time import sleep

# @pytest.fixture
# def sql():
#     return MSSQLConnector()
@pytest.fixture()
def messages():
    return RabbitMessages()

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
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 1

                mq.consume('Catalog', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 2

                body=messages.stockconfirmed()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',body=json.dumps(body))
                mq.consume('Payment', callback)
                assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 3

                body = messages.paymentsuccses()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentSucceededIntegrationEvent', body=json.dumps(body))

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

            mq.consume('Catalog', callback)
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

            mq.consume('Catalog', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
            orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 2


            body = messages.stockconfirmed()
            mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(body))
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

