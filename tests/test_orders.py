import pytest
from utils import *
import pyodbc
import json
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *

# @pytest.fixture
# def sql():
#     return MSSQLConnector()
@pytest.fixture()
def messages():
    return RabbitMessages()

@pytest.fixture()
def rabbitsend():
    return RabbitMQ()


def test_first_try(messages,rabbitsend):
    #rk=''
    productid=1
    quantity=5
    body = messages.usercheckout(productid,quantity)
    
    with MSSQLConnector() as conn:
        ordersnum=conn.select_query('SELECT COUNT(Id) from ordering.orders')
    with MSSQLConnector('CatalogDb') as conn:
        startingstock = conn.select_query(f'SELECT AvailableStock from Catalog where id ={productid}')
    #body = messages.usercheckout(5)
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',routing_key='UserCheckoutAcceptedIntegrationEvent',body=json.dumps(body))
        mq.consume('Basket', callback)
        assert returnglob() == 'OrderStartedIntegrationEvent'

        mq.consume('Catalog', callback)
        #assert routigkey[0] =='OrderStatusChangedToAwaitingValidationIntegrationEvent'
        assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

        body=messages.stockconfirmed()
        mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',body=json.dumps(body))
        mq.consume('Payment', callback)
        assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

        body = messages.paymentsuccses()
        mq.publish(exchange='eshop_event_bus', routing_key='OrderPaymentSucceededIntegrationEvent', body=json.dumps(body))

        mq.consume('Catalog', callback)
        assert returnglob() == 'OrderStatusChangedToPaidIntegrationEvent'
        #body=messages.stockconfirmed()
        #mq.publish(exchange='eshop_event_bus', routing_key='OrderStatusChangedToStockConfirmedIntegrationEvent',body=json.dumps(body))
        #assert routigkey[0]=
        with MSSQLConnector() as conn:
            result=conn.select_query('SELECT COUNT(Id) from ordering.orders')
            orderstatus=conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
    assert result[0]['']==ordersnum[0]['']+1
    assert orderstatus[0]['OrderStatusId']==4

    #with MSSQLConnector('CatalogDb') as conn:
     #   endingstock = conn.select_query(f'SELECT AvailableStock from Catalog where id ={productid}')
    #assert endingstock[0]['AvailableStock']==startingstock[0]['AvailableStock']-quantity

    #result = sql.select_query('SELECT COUNT(Id) from ordering.orders')
    #print(result)