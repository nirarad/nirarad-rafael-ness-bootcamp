import pytest
from utils import *
import pyodbc
import json
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.api.ordering_api import OrderingAPI
from utils.api.bearer_tokenizer import BearerTokenizer
from utils.rabbitmq.rabbitmq_receive import *
from time import sleep


rabbit_queues = {1: 'Basket', 2: 'Catalog', 3: 'Payment', 4: 'Ordering.signalrhub'}

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
def test_MSS(messages):
    productid = 1
    quantity = 1
    cardtype = 1
    username = 'alice'
    body = messages.usercheckout(productid, quantity, cardtype, username)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

                mq.publish(exchange='eshop_event_bus' , routing_key='UserCheckoutAcceptedIntegrationEvent' , body=json.dumps(body))

                mq.consume('Basket', callback)
                assert returnglob() == 'OrderStartedIntegrationEvent'

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'

                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 1

                mq.consume('Catalog', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                #sleep(4)
                assert orderstatus[0]['OrderStatusId'] == 2

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

                body = messages.stockconfirmed()
                mq.publish(exchange='eshop_event_bus' , routing_key='OrderStockConfirmedIntegrationEvent' , body=json.dumps(body))

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

                result = conn.select_query('SELECT COUNT(Id) from ordering.orders')
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
    assert result[0][''] == ordersnum[0]['']+1
    assert orderstatus[0]['OrderStatusId'] == 4


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

            body = messages.stockreject()
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

            #sleep(8)
            result = conn.select_query('SELECT COUNT(Id) from ordering.orders')
            while True:
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                if orderstatus[0]['OrderStatusId']!=3:
                    break
                sleep(1)
            mq.purge(rabbit_queues[4])
    assert result[0][''] == ordersnum[0][''] + 1
    assert orderstatus[0]['OrderStatusId'] == 6



@pytest.mark.test_cancel_order_status_1
def test_cancel_order_status_1(order_api,messages):
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

                mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                            body=json.dumps(messages.usercheckout()))
                #mq.consume('Basket', callback)
                #assert returnglob() == 'OrderStartedIntegrationEvent'

                #mq.consume('Ordering.signalrhub', callback)
                #assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'
                sleep(3)
                orderstatus = conn.select_query(
                    'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 1
                #sleep(3)
                orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 1')
                orderid = orderid[0]['']
                order_api.cancel_order(orderid)
                #sleep(5)
                mq.purge(rabbit_queues[1])
                mq.purge(rabbit_queues[4])
                newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    try:
        assert newstatus[0]['OrderStatusId'] == 6
        print('test_cancel_order_status_1: test pass')
    except:
        print('test_cancel_order_status_1: test fail')


@pytest.mark.test_cancel_order_status_2
def test_cancel_order_status_2(order_api,messages):
    body=messages.usercheckout()
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            mq.consume('Basket', callback)
            assert returnglob() == 'OrderStartedIntegrationEvent'

            mq.consume('Ordering.signalrhub', callback)
            assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'

            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 1

            #mq.consume('Catalog', callback)
            #assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
            while True:
                orderstatus=conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                if orderstatus[0]['OrderStatusId'] ==2:
                    break
                sleep(1)
            #sleep(10)
            assert orderstatus[0]['OrderStatusId'] == 2


            orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 2')
            orderid = orderid[0]['']
            order_api.cancel_order(orderid)
            newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
            mq.purge(rabbit_queues[4])
            mq.purge(rabbit_queues[2])
    try:
        assert newstatus[0]['OrderStatusId'] == 6
        print('test_cancel_order_status_2: test pass')
    except:
        print('test_cancel_order_status_2: test fail')


@pytest.mark.test_cancel_order_status_3
def test_cancel_order_status_3(order_api,messages):
    body=messages.usercheckout()
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
                #sleep(5)
                assert orderstatus[0]['OrderStatusId'] == 2

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

                body=messages.stockconfirmed()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

                # mq.consume('Payment', callback)
                # assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 3


                orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 3')
                orderid = orderid[0]['']
                order_api.cancel_order(orderid)
                newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
                mq.purge(rabbit_queues[4])
                mq.purge(rabbit_queues[3])
    try:
        assert newstatus[0]['OrderStatusId'] == 6
        print('test_cancel_order_status_3: test pass')
    except:
        print('test_cancel_order_status_3: test fail')

@pytest.mark.test_cancel_order_status_4_fail
def test_cancel_order_status_4_fail(order_api,messages):
    with MSSQLConnector() as conn:
        test_MSS(messages)
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 4


@pytest.mark.test_cancel_order_status_5_fail
def test_cancel_order_status_5_fail(order_api,messages):
    with MSSQLConnector() as conn:
        test_update_order_to_shiped(order_api,messages)
        orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 5')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
    assert newstatus[0]['OrderStatusId'] == 5




@pytest.mark.test_update_order_to_shiped
def test_update_order_to_shiped(order_api,messages):
    test_MSS(messages)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            orderid=conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
            orderid=orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
            mq.purge(rabbit_queues[4])
    try:
        assert newstatus[0]['OrderStatusId']==5
        print('test_update_order_to_shiped: test pass')
    except:
        print('test_update_order_to_shiped: test fail')


@pytest.mark.test_update_order_to_shiped_fail_status_1
def test_update_order_to_shiped_fail_status_1(order_api,messages):
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(messages.usercheckout()))
            # mq.consume('Basket', callback)
            # assert returnglob() == 'OrderStartedIntegrationEvent'

            # mq.consume('Ordering.signalrhub', callback)
            # assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'
            sleep(3)
            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            assert orderstatus[0]['OrderStatusId'] == 1
            # sleep(3)
            orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 1')
            orderid = orderid[0]['']

            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[4])
            newstatus = conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
        try:
            assert newstatus[0]['OrderStatusId'] == 1
            print('test_cancel_order_status_1: test pass')
        except:
            print('test_cancel_order_status_1: test fail')

@pytest.mark.test_update_order_to_shiped_fail_status_2
def test_update_order_to_shiped_fail_status_2(order_api,messages):
    body=messages.usercheckout()
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            mq.consume('Basket', callback)
            assert returnglob() == 'OrderStartedIntegrationEvent'

            while True:
                orderstatus=conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                if orderstatus[0]['OrderStatusId'] ==2:
                    break
                sleep(1)

            mq.consume('Catalog', callback)
            assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

            orderstatus = conn.select_query(
                'select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
            sleep(5)
            assert orderstatus[0]['OrderStatusId'] == 2

            orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 2')
            orderid = orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus = conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
            mq.purge(rabbit_queues[4])
        assert newstatus[0]['OrderStatusId'] == 2



@pytest.mark.test_update_order_to_shiped_fail_status_3
def test_update_order_to_shiped_fail_status_3(order_api,messages):
    body=messages.usercheckout()
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
                #sleep(5)
                assert orderstatus[0]['OrderStatusId'] == 2

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

                body=messages.stockconfirmed()
                mq.publish(exchange='eshop_event_bus', routing_key='OrderStockConfirmedIntegrationEvent',body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

                # mq.consume('Payment', callback)
                # assert returnglob() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
                orderstatus = conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                assert orderstatus[0]['OrderStatusId'] == 3


                orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 3')
                orderid = orderid[0]['']

                newstatus = conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
                mq.purge(rabbit_queues[4])
                mq.purge(rabbit_queues[3])
    try:
        assert newstatus[0]['OrderStatusId'] == 3
        print('test_cancel_order_status_3: test pass')
    except:
        print('test_cancel_order_status_3: test fail')


@pytest.mark.test_update_order_to_shiped_fail_status_6
def test_update_order_to_shiped_fail_status_6(order_api,messages):
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            test_cancel_order_status_1(order_api,messages)
            orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 6')
            orderid = orderid[0]['']
            order_api.update_to_shiped(orderid)

            while True:
                orderstatus=conn.select_query('select OrderStatusId from ordering.orders where Id = (select max(id) from ordering.orders)')
                if orderstatus[0]['OrderStatusId'] ==6:
                    break
                sleep(1)

            #newstatus = conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
    try:
        assert orderstatus[0]['OrderStatusId'] == 6
        print('test_update_order_to_shiped_fail_status_6: test pass')
    except:
        print('test_update_order_to_shiped_fail_status_6: test fail')


@pytest.mark.test_order_fail_with_card_type_4
def test_order_fail_with_card_type_4(messages):
    productid = 1
    quantity = 1
    cardtype=4
    body = messages.usercheckout(productid, quantity,cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            endingcount= conn.select_query('SELECT COUNT(Id) from ordering.orders')
    try:
        assert startcount==endingcount
        print('test_order_fail_with_card_type_4: test pass no new order has created')
    except:
        print('test_order_fail_with_card_type_4: test fail a order has been created')

@pytest.mark.test_order_fail_with_card_type_0
def test_order_fail_with_card_type_0(messages):
    productid = 1
    quantity = 1
    cardtype=0
    body = messages.usercheckout(productid, quantity,cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            endingcount= conn.select_query('SELECT COUNT(Id) from ordering.orders')
    try:
        assert startcount==endingcount
        print('test_order_fail_with_card_type_0: test pass no new order has created')
    except:
        print('test_order_fail_with_card_type_0: test fail a order has been created')

@pytest.mark.test_order_fail_with_card_type_negative
def test_order_fail_with_card_type_negative(messages):
    productid = 1
    quantity = 1
    cardtype=-1
    body = messages.usercheckout(productid, quantity,cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))

            endingcount= conn.select_query('SELECT COUNT(Id) from ordering.orders')
    try:
        assert startcount==endingcount
        print('test_order_fail_with_card_type_negative: test pass')
    except:
        print('test_order_fail_with_card_type_negative: test fail')


@pytest.mark.test_create_order_with_wrong_security_number
def test_create_order_with_wrong_security_number(messages):
    #productid = 1
    #quantity = 1
    #cardtype = -1
    cardsecuritynumber = 1234
    body = messages.usercheckout(CardSecurityNumber=cardsecuritynumber)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))
            sleep(10)
            endingcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])

    try:
        assert startcount == endingcount
        print('test_order_fail_with_card_type_negative: test pass')
    except:
        print('test_order_fail_with_card_type_negative: test fail')


@pytest.mark.test_create_order_with_wrong_credit_card_number
def test_create_order_with_wrong_credit_card_number(messages):
    cardnumber=4012888888881881
    body = messages.usercheckout()
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')

            mq.publish(exchange='eshop_event_bus', routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(body))
            sleep(5)
            #mq.consume('Basket', callback)
            #assert returnglob() == 'OrderStartedIntegrationEvent'

            #mq.consume('Ordering.signalrhub', callback)
            #assert returnglob() == 'OrderStatusChangedToSubmittedIntegrationEvent'
            endingcount = conn.select_query('SELECT COUNT(Id) from ordering.orders')
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])

    try:
        assert startcount == endingcount
        print('test_order_fail_with_card_type_negative: test pass')
    except:
        print('test_order_fail_with_card_type_negative: test fail')


def test_get_user_order_by_id(order_api,messages):
    orderid=68
    body=messages.respone_of_get_order_by_id(orderid)
    #orders=len(order_api.get_orders().json())
    respone=order_api.get_order_by_id(68).json()
    assert respone==body

def test_get_user_order_by_id_of_diffrent_user(order_api,messages):
    orderid=42
    #try:
    assert order_api.get_order_by_id(orderid).status_code==401
    #    print('test pass')
    #except:
    #    print('test fail can see a order of diffrent user')

def test_get_user_orders(order_api):
    order_api=OrderingAPI('bob','Pass123%24')
    orders=len(order_api.get_orders().json())
    assert orders==2

@pytest.mark.test_update_order_to_shiped
def test_update_order_to_shiped_to_diffrent_user(order_api,messages):
       # productid = 1
       #quantity = 1
       #cardtype = 1
       username = 'john'
       #test_MSS(messages.usercheckout(productid,quantity,cardtype,username))
       with RabbitMQ() as mq:
            with MSSQLConnector() as conn:
                #test_MSS()
                #orderid=conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
                orderid=conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4 and Id != 11')
                orderid=orderid[0]['']
                order_api.update_to_shiped(orderid)
                sleep(5)
                newstatus=conn.select_query(f'SELECT OrderStatusId from ordering.orders where Id = {orderid}')
                mq.purge(rabbit_queues[4])
        #try:
            assert newstatus[0]['OrderStatusId']==4
            #print('security test faild user can update a diffrent user order status')
        #except:
            #print('security test pass')

