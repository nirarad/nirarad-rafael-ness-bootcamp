import json
import time
from tests.messages import *
import pytest
from utils.docker import docker_utils
from utils.db.db_utils import DbUtils
from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_utils import SingleMessageConsumer
from tests.system import System


@pytest.fixture()
def system():
    system = System()
    system.init_dockers()
    system.rmq.connect()
    system.purge_all_queues()
    yield system


@pytest.fixture()
def system1():
    system1 = System()
    system1.init_dockers()
    system1.rmq.connect()
    system1.purge_all_queues()
    system1.start_basket_catalog_payment()
    yield system1


# 1
@pytest.mark.integration
def test_place_order_success(system):
    """
    test checks placing a new order full success flow
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == 'OrderStartedIntegrationEvent'
    assert basket.last_msg_body['UserId'] == USER_CHECKOUT_ACCEPTED_MESSAGE['UserId']

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert catalog.last_msg_body['OrderStockItems'][0]["ProductId"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["ProductId"]
    assert catalog.last_msg_body['OrderStockItems'][0]["Units"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["Quantity"]

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
    assert payment.last_msg_body["OrderId"] == order_id
    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 3

    ORDER_PAYMENT_SUCCEEDED_MESSAGE['OrderId'] = order_id

    # sends the payment succeed message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentSucceededIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_SUCCEEDED_MESSAGE))

    # catches the message in the catalog queue
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToPaidIntegrationEvent'
    assert catalog.last_msg_body['OrderStockItems'][0]["ProductId"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["ProductId"]
    assert catalog.last_msg_body['OrderStockItems'][0]["Units"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["Quantity"]

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 4


# 2
@pytest.mark.integration
def test_out_of_stock(system):
    """
    test place a new order with not enough items in stock message going forward
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == 'OrderStartedIntegrationEvent'
    assert basket.last_msg_body['UserId'] == USER_CHECKOUT_ACCEPTED_MESSAGE['UserId']

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert catalog.last_msg_body['OrderStockItems'][0]["ProductId"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["ProductId"]
    assert catalog.last_msg_body['OrderStockItems'][0]["Units"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["Quantity"]

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    ORDER_OUT_OF_STOCK_MESSAGE['OrderId'] = order_id

    # sends the "out of stock" message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockRejectedIntegrationEvent',
        body=json.dumps(ORDER_OUT_OF_STOCK_MESSAGE))

    time.sleep(15)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 6


# 3
@pytest.mark.integration
def test_payment_failure(system):
    """
    test place a new order with payment failure message going forward
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == 'OrderStartedIntegrationEvent'
    assert basket.last_msg_body['UserId'] == USER_CHECKOUT_ACCEPTED_MESSAGE['UserId']

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'
    assert catalog.last_msg_body['OrderStockItems'][0]["ProductId"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["ProductId"]
    assert catalog.last_msg_body['OrderStockItems'][0]["Units"] == \
           USER_CHECKOUT_ACCEPTED_MESSAGE["Basket"]["Items"][0]["Quantity"]

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
    assert payment.last_msg_body["OrderId"] == order_id

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 3

    ORDER_PAYMENT_FAILURE_MESSAGE['OrderId'] = order_id

    # sends the "payment failed" message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentFailedIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_FAILURE_MESSAGE))

    time.sleep(15)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 6


# 4
@pytest.mark.order
def test_ship_order(system):
    """
    test place a new order and checks that it can not be shipped before it gets to status paid
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    # can not be shipped from status 2
    api = OrderingAPI(NAME_ALICE, PASSWORD)
    code = api.change_status_to_shipped(order_id)
    assert code.status_code == 400

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()

    # can not be shipped from status 3
    code = api.change_status_to_shipped(order_id)
    assert code.status_code == 400

    ORDER_PAYMENT_SUCCEEDED_MESSAGE['OrderId'] = order_id

    # sends the payment succeed message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentSucceededIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_SUCCEEDED_MESSAGE))

    # catches the message in the catalog queue
    catalog.wait_for_message()

    # can be shipped from status 4
    code = api.change_status_to_shipped(order_id)
    assert code.status_code == 200

    time.sleep(1)
    x = DbUtils.statuscode_byID(order_id)
    assert x == 5


# 5
@pytest.mark.order
def test_ship_order_status6(system):
    """
    test that it is not possible to ship an order in status 6
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    api = OrderingAPI(NAME_ALICE, PASSWORD)
    # cancel the order
    api.cancel_order(order_id)

    # ship the order
    code = api.change_status_to_shipped(order_id)

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 6
    assert code.status_code == 400


# 6
@pytest.mark.order
def test_cancel_order_status2(system):
    """
    test that it is possible to cancel an order in status 2
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    api = OrderingAPI(NAME_ALICE, PASSWORD)
    code = api.cancel_order(order_id)

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 6
    assert code.status_code == 200


# 7
@pytest.mark.order
def test_cancel_order_status3(system):
    """
    test that it is possible to cancel an order in status 3
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 3

    api = OrderingAPI(NAME_ALICE, PASSWORD)
    code = api.cancel_order(order_id)

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 6
    assert code.status_code == 200


# 8
@pytest.mark.order
def test_cancel_order_status4and5(system):
    """
    tests that it is not possible to cancel an order in status 4 or 5
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()

    ORDER_PAYMENT_SUCCEEDED_MESSAGE['OrderId'] = order_id

    # sends the payment succeed message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentSucceededIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_SUCCEEDED_MESSAGE))

    # catches the message in the catalog queue
    catalog.wait_for_message()

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 4

    api = OrderingAPI(NAME_ALICE, PASSWORD)
    code = api.cancel_order(order_id)

    # can not cancel from status 4
    assert code.status_code == 400

    # shipped
    api.change_status_to_shipped(order_id)
    x = DbUtils.statuscode_byID(order_id)
    assert x == 5

    # can not cancel from status 5
    code = api.cancel_order(order_id)
    assert code.status_code == 400


# 9
@pytest.mark.tracking
def test_order_tracking(system):
    """
    test checks that the status of the order is shown properly from Awaitingvalidation to shipped
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    # login
    api = OrderingAPI(NAME_ALICE, PASSWORD)
    order = api.get_order_by_id(order_id)
    assert order.json()['status'] == 'awaitingvalidation'

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    # sends the stock confirmation message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    # catches the message in the payment queue
    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()

    order = api.get_order_by_id(order_id)
    assert order.json()['status'] == 'stockconfirmed'

    ORDER_PAYMENT_SUCCEEDED_MESSAGE['OrderId'] = order_id

    # sends the payment succeed message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentSucceededIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_SUCCEEDED_MESSAGE))

    # catches the message in the catalog queue
    catalog.wait_for_message()

    order = api.get_order_by_id(order_id)
    assert order.json()['status'] == 'paid'

    api.change_status_to_shipped(order_id)

    order = api.get_order_by_id(order_id)
    assert order.json()['status'] == 'shipped'


# 10
@pytest.mark.tracking
def test_order_tracking_cancel(system):
    """
    test checks that the status of a cancelled order is shown properly: cancelled
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    api = OrderingAPI(NAME_ALICE, PASSWORD)
    api.cancel_order(order_id)

    order = api.get_order_by_id(order_id)
    assert order.json()['status'] == 'cancelled'


# 11
@pytest.mark.scalability
def test_ordering_service_performance(system1):
    """
    test checks the performance of the uut with values equivalent to 100 messages per hour
    """

    num_requests = 5
    max_orders_id = DbUtils.get_max_orders_id()

    for i in range(num_requests):
        # a new unique uuid
        USER_CHECKOUT_ACCEPTED_MESSAGE["RequestId"] = str(uuid.uuid4())
        system1.rmq.publish(
            exchange='eshop_event_bus',
            routing_key='UserCheckoutAcceptedIntegrationEvent',
            body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    timeout = (60 * 60) / 100 * num_requests
    while timeout > 0:
        done = True
        orders = DbUtils.get_orders_greater_than_id(max_orders_id)
        if len(orders) != num_requests:
            done = False
        else:
            for o in orders:
                if o["OrderStatusId"] != 4:
                    done = False
                    break
        if done:
            break
        sleep = 10
        time.sleep(sleep)
        timeout -= sleep

    assert timeout > 0, 'Timeout waiting for all orders to complete'


# 12
@pytest.mark.stock
def test_stock_update(system1):
    """
    test checks that the stock is updated after an order is completed and gets to status paid
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    stock_before_order = DbUtils.get_item_quantity(1)

    # sends the order message
    system1.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    time.sleep(180)
    stock_after_order = DbUtils.get_item_quantity(1)
    assert stock_after_order < stock_before_order


# 13
@pytest.mark.orderdata
def test_wrong_card_type(system1):
    """
    test checks placing a new order with card type that is not in the system (1,2,3)
    """
    max_order_id_start = DbUtils.get_max_orders_id()

    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())
    USER_CHECKOUT_ACCEPTED_MESSAGE['CardTypeId'] = CARD_TYPE

    # sends the order message
    system1.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    max_order_id_end = DbUtils.get_max_orders_id()

    assert max_order_id_start == max_order_id_end


# 14
@pytest.mark.orderdata
def test_zero_quantity(system1):
    """
    test checks placing a new order with item with 0 quantity
    """
    max_order_id_start = DbUtils.get_max_orders_id()

    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())
    # quantity=0
    USER_CHECKOUT_ACCEPTED_MESSAGE['Basket']['Items'][0]['Quantity'] = 0

    # sends the order message
    system1.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    max_order_id_end = DbUtils.get_max_orders_id()

    assert max_order_id_start == max_order_id_end


# 15
@pytest.mark.security
def test_security1(system1):
    """
    test checks that a user can see only his orders and not another user orders
    """

    api = OrderingAPI(NAME_ALICE, PASSWORD)

    time.sleep(1)

    orders1 = api.get_orders()
    orders2 = DbUtils.get_orders_id(11)
    assert len(orders1) == len(orders2)
    for i in range(len(orders1)):
        assert orders1[i]['ordernumber'] == orders2[i]['Id']


# 16
@pytest.mark.security
def test_security2(system):
    """
    test checks that a user can not cancel an order of another user
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    # sends the order message
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    # catches the message in the basket queue
    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()

    # catches the message in the catalog queue
    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()

    # saves the orderid from the message in the catalog queue
    order_id = catalog.last_msg_body['OrderId']

    api = OrderingAPI(NAME_BOB, PASSWORD)
    code = api.cancel_order(order_id)

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert code.status_code == 400
    assert x == 2


# 17
@pytest.mark.reliablity
def test_ordering_service_reliability(system):
    """
    test place a new order full success flow and test the recovery of the uut before each message
    """
    # a new unique uuid
    USER_CHECKOUT_ACCEPTED_MESSAGE['RequestId'] = str(uuid.uuid4())

    dm = docker_utils.DockerManager()

    def stop_ordering():
        dm.stop('eshop/ordering.api:linux-latest')

    def start_ordering():
        dm.start('eshop/ordering.api:linux-latest')

    start_ordering()
    stop_ordering()
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='UserCheckoutAcceptedIntegrationEvent',
        body=json.dumps(USER_CHECKOUT_ACCEPTED_MESSAGE))

    start_ordering()

    basket = SingleMessageConsumer('Basket')
    basket.wait_for_message()
    assert basket.last_msg_method.routing_key == 'OrderStartedIntegrationEvent'

    catalog = SingleMessageConsumer('Catalog')
    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

    order_id = catalog.last_msg_body['OrderId']

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 2

    ORDER_STOCK_CONFIRMED_MESSAGE['OrderId'] = order_id

    stop_ordering()
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderStockConfirmedIntegrationEvent',
        body=json.dumps(ORDER_STOCK_CONFIRMED_MESSAGE))

    start_ordering()

    payment = SingleMessageConsumer('Payment')
    payment.wait_for_message()
    assert payment.last_msg_method.routing_key == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 3

    stop_ordering()

    ORDER_PAYMENT_SUCCEEDED_MESSAGE['OrderId'] = order_id
    system.rmq.publish(
        exchange='eshop_event_bus',
        routing_key='OrderPaymentSucceededIntegrationEvent',
        body=json.dumps(ORDER_PAYMENT_SUCCEEDED_MESSAGE))

    start_ordering()

    catalog.wait_for_message()
    assert catalog.last_msg_method.routing_key == 'OrderStatusChangedToPaidIntegrationEvent'

    time.sleep(1)

    x = DbUtils.statuscode_byID(order_id)
    assert x == 4
