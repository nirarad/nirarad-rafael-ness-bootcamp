import os
import pytest
import json
import time
from dotenv import load_dotenv
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages
from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_receive import *
from time import sleep
from utils.docker.docker_utils import DockerManager


load_dotenv()
usercheckout=os.getenv('USERCHECKOUT')
exchange=os.getenv('EXCHANGE')
instock=os.getenv('STOCKCONFIRMERD')
stockreject=os.getenv('STOCKREJECT')
paymentfail=os.getenv('PAYMENTFAIL')
paymentsucceeded=os.getenv('PAYMENTSUCCEEDED')

orderstart=os.getenv('ORDERSTART')
statussubmitted=os.getenv('STATUSSUBMITTED')
statusawaiting=os.getenv('STATUSAWAITING')
statusstockconfirmed=os.getenv('STATUSSTOCKCONFIRMED')
statuspaid=os.getenv('STATUSPAID')

dockerflag=0

submitted=int(os.getenv('SUBMITTED'))
awaitingvalidation=int(os.getenv('AWAITINGVALIDATION'))
stockconfirmerd=int(os.getenv('STOCKCONFIRMED'))
paid=int(os.getenv('PAID'))
shipped=int(os.getenv('SHIPPED'))
cancelled=int(os.getenv('CANCELLED'))

currentstatus=os.getenv('CURRENTSTATUS')
orderidbystatus=os.getenv('ORDERIDBYSTATUS')
totalorderscount=os.getenv('TOTALORDERSCOUNT')
orderstatusbyid=os.getenv('ORDERSTATUSBYID')





rabbit_queues = {1: 'Basket', 2: 'Catalog', 3: 'Payment', 4: 'Ordering.signalrhub'}




@pytest.fixture()
def docker():
    return DockerManager()

@pytest.fixture()
def messages():
    return RabbitMessages()


@pytest.fixture()
def order_api():
    return OrderingAPI()


@pytest.fixture()
def rabbitsend():
    return RabbitMQ()




@pytest.mark.test_ordering_api_load_performance
def test_ordering_api_load_performance(order_api, messages,docker):
    '''
      writer: shlomo mhadker
      date:14.3.2023
     test number 30: stop ordering api service send a 100 create a new order requests
     start ordering api service again we expect that the process will create a new 100 orders in
     less than 1 hour
    '''

    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                docker.stop('eshop/ordering.api:linux-latest')
                orderstart=conn.select_query(totalorderscount)
                for i in range(100):
                    body=messages.usercheckout()
                    mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
                sleep(30)
                docker.start('eshop/ordering.api:linux-latest')
                sleep(30)
                start_time = time.time()
                laststatus = conn.select_query(currentstatus)
                while laststatus[0]['OrderStatusId']!=paid:
                    laststatus = conn.select_query(currentstatus)
                    sleep(5)
                elapsed_time = time.time() - start_time
                orderendsnum = conn.select_query(totalorderscount)
                docker.stop_services()
                sleep(30)
    assert elapsed_time<=3600
    assert orderstart[0][''] + 100 == orderendsnum[0]['']

@pytest.mark.test_MSS
def test_MSS(messages,docker,crash=0,stockfail=0,paymentfailf=0):
    '''
    writer: shlomo mhadker
    date:14.3.2023
    test number 1: with default param create a new order flow MSS
    '''
    body = messages.usercheckout()
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                ordersnum = conn.select_query(totalorderscount)

                mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
                #docker.start('eshop/ordering.api:linux-latest')
                mq.consume('Basket', callback)
                assert returnglob() == orderstart

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == statussubmitted

                orderstatus = conn.select_query(currentstatus)
                assert orderstatus[0]['OrderStatusId'] == submitted

                mq.consume('Catalog', callback)
                assert returnglob() == statusawaiting
                orderstatus = conn.select_query(currentstatus)
                #sleep(4)
                assert orderstatus[0]['OrderStatusId'] == awaitingvalidation
                if crash==1:
                    docker.stop('eshop/ordering.api:linux-latest')
                    sleep(30)
                    docker.start('eshop/ordering.api:linux-latest')

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == statusawaiting
                if stockfail==1:
                    body = messages.stockreject()
                    mq.publish(exchange=exchange, routing_key=stockreject,body=json.dumps(body))
                    return 1

                body = messages.stockconfirmed()
                mq.publish(exchange=exchange , routing_key=instock , body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == statusstockconfirmed

                mq.consume('Payment', callback)
                assert returnglob() == statusstockconfirmed
                orderstatus = conn.select_query(currentstatus)
                assert orderstatus[0]['OrderStatusId'] == stockconfirmerd
                if paymentfailf==1:
                    body = messages.paymentfail()
                    mq.publish(exchange=exchange, routing_key=paymentfail,body=json.dumps(body))
                    return
                body = messages.paymentsuccses()
                mq.publish(exchange=exchange, routing_key=paymentsucceeded, body=json.dumps(body))

                mq.consume('Ordering.signalrhub', callback)
                assert returnglob() == statuspaid

                mq.consume('Catalog', callback)
                assert returnglob() == statuspaid

                result = conn.select_query(totalorderscount)
                orderstatus = conn.select_query(currentstatus)
    assert result[0][''] == ordersnum[0]['']+1
    assert orderstatus[0]['OrderStatusId'] == paid


@pytest.mark.test_outofstock
def test_outofstock(messages,docker,cancel=0):
    '''
    writer: shlomo mhadker
    date:14.3.2023
    test number 2: try to create order with not enough product quantity (using test 1)
    '''

    with MSSQLConnector() as conn:
            result=test_MSS(messages,docker,stockfail=1)
            while True:
                orderstatus = conn.select_query(currentstatus)
                if orderstatus[0]['OrderStatusId']==awaitingvalidation and cancel==1:
                    return orderstatus[0]['OrderStatusId']
                if orderstatus[0]['OrderStatusId']!=awaitingvalidation:
                    break
                sleep(1)
    assert orderstatus[0]['OrderStatusId'] == cancelled


@pytest.mark.test_paymentfail
def test_paymentfail(messages,docker,cancel=0):
    '''
    writer: shlomo mhadker
    date:14.3.2023
    test number 3: try to create order with a payment fail (using test 1)
    '''
    with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            test_MSS(messages,docker,paymentfailf=1)
            while True:
                orderstatus = conn.select_query(currentstatus)
                if orderstatus[0]['OrderStatusId'] ==stockconfirmerd and cancel==1:
                    return orderstatus
                if orderstatus[0]['OrderStatusId'] != stockconfirmerd:
                    break
                sleep(1)
                mq.purge(rabbit_queues[4])
    assert orderstatus[0]['OrderStatusId'] == cancelled



@pytest.mark.test_cancel_order_status_1
def test_cancel_order_status_1(order_api,messages):
    '''
    writer: shlomo mhadker
    date:14.3.2023
    test number 4: cancel an order that her current status is submitted
    '''
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
                ordersnum = conn.select_query(totalorderscount)

                mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(messages.usercheckout()))
                sleep(3)
                orderstatus = conn.select_query(currentstatus)
                assert orderstatus[0]['OrderStatusId'] == submitted
                orderid = conn.select_query(f'{orderidbystatus}{submitted}')
                orderid = orderid[0]['']
                order_api.cancel_order(orderid)
                mq.purge(rabbit_queues[1])
                mq.purge(rabbit_queues[4])
                newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')

        assert newstatus[0]['OrderStatusId'] == cancelled



@pytest.mark.test_cancel_order_status_2
def test_cancel_order_status_2(order_api,messages,docker,update=0):
    '''
    writer: shlomo mhadker
    date:14.3.2023
    test number 5: cancel an order that her current status is awaitingvalidation (using test 2)
    '''
    orderstatus=test_outofstock(messages,docker,cancel=1)
    #sleep(10)
    assert orderstatus== awaitingvalidation
    if update==1:
        return orderstatus
    with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            orderid = conn.select_query(f'{orderidbystatus}{awaitingvalidation}')
            orderid = orderid[0]['']
            order_api.cancel_order(orderid)
            newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')
            mq.purge(rabbit_queues[4])
            mq.purge(rabbit_queues[2])

    assert newstatus[0]['OrderStatusId'] == cancelled



@pytest.mark.test_cancel_order_status_3
def test_cancel_order_status_3(order_api,messages,docker,update=0):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 6: cancel an order that her current status is stock confirmerd (using tes 3)
     '''
    orderstatus=test_paymentfail(messages,docker,cancel=1)
    assert orderstatus[0]['OrderStatusId'] == stockconfirmerd
    if update==1:
        return orderstatus
    with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            orderid = conn.select_query(f'{orderidbystatus}{stockconfirmerd}')
            orderid = orderid[0]['']
            order_api.cancel_order(orderid)
            newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')

            mq.purge(rabbit_queues[4])
            mq.purge(rabbit_queues[3])
    assert newstatus[0]['OrderStatusId'] == cancelled



@pytest.mark.test_cancel_order_status_4_fail
def test_cancel_order_status_4_fail(order_api,messages,docker):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 7:try to cancel an order that her current status is paid (using test 1)
     '''
    with MSSQLConnector() as conn:
        test_MSS(messages,docker)
        orderid = conn.select_query(f'{orderidbystatus} {paid}')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'{orderstatusbyid}{orderid}')
    assert newstatus[0]['OrderStatusId'] == paid


@pytest.mark.test_update_order_to_shiped
def test_update_order_to_shiped(order_api,messages,docker):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 8:create order and then update the order status from paid to shipped
     '''

    test_MSS(messages,docker)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            orderid=conn.select_query(f'{orderidbystatus} {paid}')
            orderid=orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')
            mq.purge(rabbit_queues[4])
        assert newstatus[0]['OrderStatusId']==shipped


@pytest.mark.test_cancel_order_status_5_fail
def test_cancel_order_status_5_fail(order_api,messages,docker):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 9:try to cancel an order that her current status is shipped (using test 8)
     '''

    with MSSQLConnector() as conn:
        test_update_order_to_shiped(order_api,messages,docker)
        orderid = conn.select_query(f'{orderidbystatus} {shipped}')
        orderid = orderid[0]['']
        order_api.cancel_order(orderid)
        newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')
    assert newstatus[0]['OrderStatusId'] == shipped




@pytest.mark.test_update_order_to_shiped_fail_status_1
def test_update_order_to_shiped_fail_status_1(order_api,messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 10:create order and then try to update the order status from submitted to shipped
     '''

    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            ordersnum = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(messages.usercheckout()))
            sleep(3)

            orderstatus = conn.select_query(currentstatus)
            assert orderstatus[0]['OrderStatusId'] == submitted

            orderid = conn.select_query(f'{orderidbystatus}{submitted}')
            orderid = orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus = conn.select_query(f'{orderstatusbyid} {orderid}')
            assert newstatus[0]['OrderStatusId'] == submitted
            sleep(60)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])


@pytest.mark.test_update_order_to_shiped_fail_status_2
def test_update_order_to_shiped_fail_status_2(order_api,messages,docker):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 11: create order and then try to update the order status from awaitingvalidation to shipped
     (using test No.5)
     '''
    with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            sleep(5)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
            orderstatus=test_cancel_order_status_2(order_api,messages,docker,update=1)
            assert orderstatus == awaitingvalidation

            orderid = conn.select_query(f'{orderidbystatus} {orderstatus}')
            orderid = orderid[0]['']
            order_api.update_to_shiped(orderid)
            newstatus = conn.select_query(f'{orderstatusbyid} {orderid}')
            mq.purge(rabbit_queues[4])
        assert newstatus[0]['OrderStatusId'] == awaitingvalidation



@pytest.mark.test_update_order_to_shiped_fail_status_3
def test_update_order_to_shiped_fail_status_3(order_api,messages,docker):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 12: create order and then try to update the order status from stockconfirmerd to shipped
     (using test No.6)
     '''
    orderstatus = test_cancel_order_status_3(order_api, messages, docker, update=1)
    assert orderstatus[0]['OrderStatusId'] == 3

    with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            orderid = conn.select_query(f'{orderidbystatus}{stockconfirmerd}')
            orderid = orderid[0]['']

            newstatus = conn.select_query(f'{orderstatusbyid} {orderid}')
            mq.purge(rabbit_queues[4])
            mq.purge(rabbit_queues[3])
            assert newstatus[0]['OrderStatusId'] == stockconfirmerd


@pytest.mark.test_update_order_to_shiped_fail_status_6
def test_update_order_to_shiped_fail_status_6(order_api,messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 13: create order and then try to update the order status from cancelled to shipped
     (using test No.4)
     '''
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            test_cancel_order_status_1(order_api,messages)
            orderid = conn.select_query(f'{orderidbystatus}{cancelled}')
            orderid = orderid[0]['']
            order_api.update_to_shiped(orderid)

            while True:
                orderstatus=conn.select_query(currentstatus)
                if orderstatus[0]['OrderStatusId'] ==cancelled:
                    break
                sleep(1)

            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert orderstatus[0]['OrderStatusId'] == cancelled



@pytest.mark.test_order_fail_with_card_type_4
def test_order_fail_with_card_type_4(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 14: try to create an order with wrong card type
     '''
    cardtype=4
    body = messages.usercheckout(cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))

            endingcount= conn.select_query(totalorderscount)
        assert startcount==endingcount


@pytest.mark.test_order_fail_with_card_type_0
def test_order_fail_with_card_type_0(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 15: try to create an order with wrong card type
     '''
    cardtype=0
    body = messages.usercheckout(cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,
                       body=json.dumps(body))

            endingcount= conn.select_query(totalorderscount)
        assert startcount==endingcount

@pytest.mark.test_order_fail_with_card_type_negative
def test_order_fail_with_card_type_negative(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 16: try to create an order with negtive card type
     '''
    cardtype=-1
    body = messages.usercheckout(cardtype)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))

            endingcount= conn.select_query(totalorderscount)
        assert startcount==endingcount



@pytest.mark.test_create_order_with_wrong_security_number
def test_create_order_with_wrong_security_number(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 17: try to create an order with wrong security number
     '''

    cardsecuritynumber = '1234'
    body = messages.usercheckout(cardsecuritynumber=cardsecuritynumber)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
            sleep(10)
            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount



@pytest.mark.test_create_order_with_wrong_credit_card_number
def test_create_order_with_wrong_credit_card_number(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 18: try to create an order with wrong credit card number
     '''

    cardnumber='4012888888881881145'
    body = messages.usercheckout(cardnumber=cardnumber)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)
            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
            sleep(7)
            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount[0][''] == endingcount[0]['']

@pytest.mark.test_create_order_with_wrong_credit_card_number_low
def test_create_order_with_wrong_credit_card_number_low(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 19: try to create an order with low number amount in credit card number
     '''

    cardnumber='4'
    body = messages.usercheckout(cardnumber=cardnumber)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,
                       body=json.dumps(body))
            sleep(7)

            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount


@pytest.mark.test_create_order_with_wrong_characters_credit_card_number
def test_create_order_with_wrong_characters_credit_card_number(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 20: try to create an order with characters insted of numbers in credit card number
     '''

    cardnumber='fkjdhsgks'
    body = messages.usercheckout(cardnumber=cardnumber)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,
                       body=json.dumps(body))
            sleep(8)

            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount


@pytest.mark.test_create_order_with_wrong_expiration_date_year
def test_create_order_with_wrong_expiration_date_year(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 21: try to create an order with invalid year in card expiration date
     '''

    year='2015'
    body = messages.usercheckout(year=year)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)

            mq.publish(exchange=exchange, routing_key=usercheckout,
                       body=json.dumps(body))
            sleep(8)

            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount


@pytest.mark.test_create_order_with_wrong_expiration_date_month
def test_create_order_with_wrong_expiration_date_month(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 22: try to create an order with invalid month in card expiration date
     '''

    month='13'
    body = messages.usercheckout(month=month)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)
            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
            sleep(8)
            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount

@pytest.mark.test_create_order_with_wrong_expiration_date_day
def test_create_order_with_wrong_expiration_date_day(messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 23: try to create an order with invalid day in card expiration date
     '''

    day='35'
    body = messages.usercheckout(day=day)
    with MSSQLConnector() as conn:
        with RabbitMQ() as mq:
            startcount = conn.select_query(totalorderscount)
            mq.publish(exchange=exchange, routing_key=usercheckout,body=json.dumps(body))
            sleep(8)
            endingcount = conn.select_query(totalorderscount)
            mq.purge(rabbit_queues[1])
            mq.purge(rabbit_queues[2])
            mq.purge(rabbit_queues[4])
        assert startcount == endingcount


@pytest.mark.test_get_user_order_by_id
def test_get_user_order_by_id(order_api,messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 24: getting order details using the order id
     '''

    orderid=68
    body=messages.respone_of_get_order_by_id(orderid)
    respone=order_api.get_order_by_id(68).json()
    assert order_api.get_order_by_id(68).status_code==200
    assert respone==body


@pytest.mark.test_get_user_orders
def test_get_user_orders(order_api):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 25: getting all orders details that a user has made
     '''

    order_api=OrderingAPI('bob','Pass123%24')
    orders=len(order_api.get_orders().json())
    assert orders==2

def test_get_user_order_by_id_of_diffrent_user(order_api,messages):
    '''
     writer: shlomo mhadker
     date:14.3.2023
     test number 26: try to get a different user order details
     '''

    orderid=42
    assert order_api.get_order_by_id(orderid).status_code==401


@pytest.mark.test_update_order_to_shiped
def test_update_order_to_shiped_to_diffrent_user(order_api,messages):
   '''
     writer: shlomo mhadker
     date:14.3.2023
    test number 27: try to update a different user order status
   '''

   with RabbitMQ() as mq:
        with MSSQLConnector() as conn:
            #orderid=conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId = 4')
            orderid=conn.select_query(f'{orderidbystatus}{paid} and Id != 11')
            orderid=orderid[0]['']
            order_api.update_to_shiped(orderid)
            sleep(5)
            newstatus=conn.select_query(f'{orderstatusbyid} {orderid}')
            mq.purge(rabbit_queues[4])
        assert newstatus[0]['OrderStatusId']==paid

@pytest.mark.test_cancel_order_to_diffrent_user
def test_cancel_order_to_diffrent_user(order_api, messages):
   '''
     writer: shlomo mhadker
     date:14.3.2023
    test number 28: try to cancel a different user order
   '''

   with RabbitMQ() as mq:
       with MSSQLConnector() as conn:
           orderid = conn.select_query('SELECT MAX(Id) from ordering.orders where orders.OrderStatusId in(1,2,3) and Id != 11')
           orderid = orderid[0]['']
           order_api.cancel_order(orderid)
           sleep(5)
           newstatus = conn.select_query(f'{orderstatusbyid} {orderid}')
           mq.purge(rabbit_queues[4])
       assert newstatus[0]['OrderStatusId'] == awaitingvalidation

@pytest.mark.test_ordering_api_crash
def test_ordering_api_crash(order_api, messages,docker):
    '''
      writer: shlomo mhadker
      date:14.3.2023
     test number 29: while a order create process is running stop ordering api service wait some timme
     and start ordering api service again,we expect that the process will continue from where it stops
     (using test No.1)
    '''
    with MSSQLConnector() as conn:
        orderstartsnum = conn.select_query(totalorderscount)
        global dockerflag
        test_MSS(messages,docker,crash=1)
        orderendsnum = conn.select_query(totalorderscount)
        assert orderstartsnum[0]['']+1==orderendsnum[0]['']
        status = conn.select_query(f'{currentstatus}')
    assert status[0]['OrderStatusId']==paid





