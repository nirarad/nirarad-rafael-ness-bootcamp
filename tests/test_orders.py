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
    rk=''
    body = messages.usercheckout()
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
    assert int(result[0][''])==129
    #result = sql.select_query('SELECT COUNT(Id) from ordering.orders')
    #print(result)