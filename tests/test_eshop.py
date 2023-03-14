# pytest test_eshop.py/ --html-report=./report
import time

import pytest

from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_receive import callback
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from tests.server_response import *
from utils.rabbitmq.rabbitmq_receive import *

ordering_api_container = 'eshop/ordering.api:linux-latest'
ordering_background_container = "eshop/ordering.backgroundtasks:linux-latest"


@pytest.fixture()
def order_api():
    """
    init the ordering api object
    """
    return OrderingAPI()


@pytest.fixture()
def docker_manager():
    """
    init the docker manager
    """
    return DockerManager()

    ####################################################################################
    #                                   Sanity test                                    #
    ####################################################################################


####################
#      Test 1      #
####################
@pytest.mark.call_the_orderingAPI
def test_call_the_ordering_api(order_api):
    """
    Test 1: Call the ordering-API.
    see test case eshop document.
    """
    assert order_api.call_server() == ok_status_code


####################
#      Test 2      #
####################
@pytest.mark.get_users_order
def test_get_users_order(order_api):
    """
    Test 2: Get user’s order.
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        assert order_api.get_order_by_id(conn.select_query(query)[0]["Id"]).json() == user_order


####################
#      Test 3      #
####################
@pytest.mark.get_users_all_order
def test_get_users_all_order(order_api):
    """
    Test 3: Get user’s all order
    see test case eshop document.
    """
    assert order_api.get_orders().json() == orders_list


####################
#      Test 4      #
####################
@pytest.mark.create_new_order
def test_create_new_order(order_api, docker_manager):
    """
    Test 4: Create new order
    see test case eshop document.
    """
    # Step 1
    all_orders = 'SELECT * from ordering.orders'
    with MSSQLConnector() as sql:
        length_before_new_order = len(sql.select_query(all_orders))
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(input_massage1_test4))
            mq.consume('Basket', callback)
            assert return_glob() == "OrderStartedIntegrationEvent"
            length_after_new_order = len(sql.select_query(all_orders))
            assert length_before_new_order < length_after_new_order
        with RabbitMQ() as mq:
            mq.consume('Catalog', callback)
            assert "OrderStatusChangedToAwaitingValidationIntegrationEvent" == return_glob()
        # Step 2
        id = sql.select_query("SELECT max(Id) FROM ordering.orders")[0]['']
        input_massage2_test4["OrderId"] = id
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(input_massage2_test4))
            mq.consume('Payment', callback)
            assert "OrderStatusChangedToStockConfirmedIntegrationEvent" == return_glob()
        # Step 3
        input_massage6_test4["OrderId"] = id
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderPaymentSucceededIntegrationEvent',
                       body=json.dumps(input_massage6_test4))
        with RabbitMQ() as mq:
            mq.consume('Catalog', callback)
            assert "OrderStatusChangedToPaidIntegrationEvent" == return_glob()

    ######################################################################################
    #                                Non functional test                                 #
    ######################################################################################


####################
#      Test 5      #
####################
@pytest.mark.ordering_server_is_crashed
def test_ordering_server_is_crashed(order_api, docker_manager):
    """
    Test 5: Ordering-API server is crashed
    see test case eshop document.
    """
    all_orders = 'SELECT * from ordering.orders'
    with MSSQLConnector() as sql:
        length_before_new_order = len(sql.select_query(all_orders))
    docker_manager.stop(ordering_api_container)
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key='UserCheckoutAcceptedIntegrationEvent',
                   body=json.dumps(input_massage1_test4))
    docker_manager.start(ordering_api_container)
    time.sleep(5)
    with MSSQLConnector() as sql:
        length_after_new_order = len(sql.select_query(all_orders))
    assert length_before_new_order + 1 == length_after_new_order


####################
#      Test 6      #
####################
@pytest.mark.a100_orders_in_one_hour
def test_100_orders_in_one_hour(order_api, docker_manager):
    """
    Test 6: 100 orders in one hour
    see test case eshop document.
    """
    all_orders = 'SELECT * from ordering.orders'
    with MSSQLConnector() as sql:
        length_before_new_order = len(sql.select_query(all_orders))
    docker_manager.stop(ordering_api_container)
    for i in range(5):
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(input_massage1_test4))
    docker_manager.start(ordering_api_container)
    time.sleep(10)
    with MSSQLConnector() as sql:
        length_after_new_order = len(sql.select_query(all_orders))
    assert length_before_new_order + 5 == length_after_new_order

    ######################################################################################
    #                                   Integration test                                 #
    ######################################################################################


####################
#      Test 7      #
####################
@pytest.mark.cancel_order_with_submitted_status
def test_cancel_order_with_submitted_status(order_api, docker_manager):
    """
    Test 7: Cancel order with submitted status
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders where OrderStatusId = 1"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        else:
            order_to_cancel = conn.select_query(query)[0]["Id"]
    docker_manager.stop(ordering_background_container)
    assert order_api.cancel_order(order_to_cancel).status_code == ok_status_code
    with MSSQLConnector() as conn:
        order_status_id = \
            conn.select_query('SELECT * from ordering.orders where Id = ' +
                              str(order_to_cancel))[0]['OrderStatusId']
    docker_manager.start(ordering_background_container)
    assert order_status_id == Cancelled


####################
#      Test 8      #
####################
@pytest.mark.create_new_order_with_invalid_payment_card
def test_create_new_order_with_invalid_payment_card(order_api):
    """
    Test 8: Create new order with invalid payment card
    see test case eshop document.
    """
    # Step 1
    all_orders = 'SELECT * from ordering.orders'
    with MSSQLConnector() as sql:
        length_before_new_order = len(sql.select_query(all_orders))
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(input_massage1_test4))
            mq.consume('Basket', callback)
            assert return_glob() == "OrderStartedIntegrationEvent"
            length_after_new_order = len(sql.select_query(all_orders))
            assert length_before_new_order < length_after_new_order
        with RabbitMQ() as mq:
            mq.consume('Catalog', callback)
            assert "OrderStatusChangedToAwaitingValidationIntegrationEvent" == return_glob()
        # Step 2
        id = sql.select_query("SELECT max(Id) FROM ordering.orders")[0]['']
        input_massage2_test4["OrderId"] = id
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(input_massage2_test4))
            mq.consume('Payment', callback)
            assert "OrderStatusChangedToStockConfirmedIntegrationEvent" == return_glob()
        # Step 3
        input_massage6_test4["OrderId"] = id
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderPaymentSucceededIntegrationEvent',
                       body=json.dumps(input_massage6_test4))
        status = sql.select_query("SELECT * FROM ordering.orders where Id = " + str(id))
        status = status[0]["OrderStatusId"]
        assert status == Cancelled


####################
#      Test 9      #
####################
@pytest.mark.create_new_order_when_the_products_are_out_of_stock
def test_create_new_order_when_the_products_are_out_of_stock(order_api):
    """
    Test 9: Create new order when the products are out of stock
    see test case eshop document.
    """
    # Step 1
    all_orders = 'SELECT * from ordering.orders'
    with MSSQLConnector() as sql:
        length_before_new_order = len(sql.select_query(all_orders))
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(input_massage1_test4))
            mq.consume('Basket', callback)
            assert return_glob() == "OrderStartedIntegrationEvent"
            length_after_new_order = len(sql.select_query(all_orders))
            assert length_before_new_order < length_after_new_order
        with RabbitMQ() as mq:
            mq.consume('Catalog', callback)
            assert "OrderStatusChangedToAwaitingValidationIntegrationEvent" == return_glob()
        # Step 2
        id = sql.select_query("SELECT max(Id) FROM ordering.orders")[0]['']
        input_massage2_test4["OrderId"] = id
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockRejectedIntegrationEvent',
                       body=json.dumps(input_massage3_test9))
        status = sql.select_query("SELECT * FROM ordering.orders where Id = " + str(id))
        status = status[0]["OrderStatusId"]
        assert status == Cancelled


#####################
#      Test 10      #
#####################
@pytest.mark.remove_invalid_order_wrong_address
def test_remove_invalid_order_wrong_address(order_api):
    """
    Test 10: Remove invalid order – wrong address
    see test case eshop document.
    """
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key='UserCheckoutAcceptedIntegrationEvent',
                   body=json.dumps(input_massage1_test10))
    time.sleep(10)
    query = "SELECT * FROM ordering.orders WHERE Id = (SELECT max(Id) FROM ordering.orders)"
    with MSSQLConnector() as conn:
        for i in range(15):
            time.sleep(5)
            order_status_id = \
                conn.select_query(query)[0]['OrderStatusId']
            if order_status_id == 6:
                break
    assert order_status_id == 6


#####################
#      Test 11      #
#####################
@pytest.mark.cancel_order_with_awaitingvalidation_status
def test_cancel_order_with_awaitingvalidation_status(order_api):
    """
    Test 11: Cancel order with "awaitingvalidation" status
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders where OrderStatusId = 2"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        else:
            order_to_cancel = conn.select_query(query)[0]["Id"]
    assert order_api.cancel_order(order_to_cancel).status_code == ok_status_code
    with MSSQLConnector() as conn:
        order_status_id = \
            conn.select_query('SELECT * from ordering.orders where Id = ' +
                              str(order_to_cancel))[0]['OrderStatusId']
    assert order_status_id == Cancelled


#####################
#      Test 12      #
#####################
@pytest.mark.cancel_order_with_stockconfirmed_status
def test_cancel_order_with_stockconfirmed_status(order_api):
    """
    Test 12: Cancel order with "stockconfirmed“ status
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders where OrderStatusId = 3"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        else:
            order_to_cancel = conn.select_query(query)[0]["Id"]
    assert order_api.cancel_order(order_to_cancel).status_code == ok_status_code
    with MSSQLConnector() as conn:
        order_status_id = \
            conn.select_query('SELECT * from ordering.orders where Id = ' +
                              str(order_to_cancel))[0]['OrderStatusId']
    assert order_status_id == Cancelled


#####################
#      Test 13      #
#####################
@pytest.mark.cancel_order_with_paid_status
def test_cancel_order_with_paid_status(order_api):
    """
    Test 13: Cancel order with paid status
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders where OrderStatusId = 4"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        else:
            order_to_cancel = conn.select_query(query)[0]["Id"]
    assert order_api.cancel_order(order_to_cancel).status_code == bad_status_code
    with MSSQLConnector() as conn:
        order_status_id = \
            conn.select_query('SELECT * from ordering.orders where Id = ' +
                              str(order_to_cancel))[0]['OrderStatusId']
    assert order_status_id == Paid


#####################
#      Test 14      #
#####################
@pytest.mark.cancel_order_with_shipped_status
def test_cancel_order_with_shipped_status(order_api):
    """
    Test 14: Cancel order with “shipped” status
    see test case eshop document.
    """
    query = "SELECT * FROM ordering.orders where OrderStatusId = 5"
    with MSSQLConnector() as conn:
        if len(conn.select_query(query)) == 0:
            pytest.skip("No record for execute this test")
        else:
            order_to_cancel = conn.select_query(query)[0]["Id"]
    assert order_api.cancel_order(order_to_cancel).status_code == bad_status_code
    with MSSQLConnector() as conn:
        order_status_id = \
            conn.select_query('SELECT * from ordering.orders where Id = ' +
                              str(order_to_cancel))[0]['OrderStatusId']
    assert order_status_id == Shipped


#####################
#      Test 15      #
#####################
@pytest.mark.reject_get_order_request_with_wrong_order_id
def test_reject_get_order_request_with_wrong_order_id(order_api):
    """
    Test 15: Reject get order request with wrong order id
    see test case eshop document.
    """
    assert order_api.get_order_by_id(10010).status_code == not_found_status_code


#####################
#      Test 16      #
#####################
@pytest.mark.reject_user_get_request_with_invalid_token
def test_reject_user_get_request_with_invalid_token(order_api):
    """
    Test 16: Reject user get request with invalid token
    see test case eshop document.
    """
    assert order_api.get_order_by_id(1, auth=False).status_code == unauthorized_status_code


#####################
#      Test 17      #
#####################
@pytest.mark.ordering_server_cancel_order_when_the_payment_failed
def test_ordering_server_cancel_order_when_the_payment_failed(order_api):
    """
    Test 17: Ordering-API server set OrderStatusID = 6 (cancel order) when the payment failed
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders where OrderStatusId = 3"
    with MSSQLConnector() as conn:
        orders_list_from_table = conn.select_query(query)
        if len(orders_list_from_table) == 0:
            pytest.skip("No record for execute this test")
        else:
            query = \
                "SELECT name from ordering.[buyers] where Id = " + str(orders_list_from_table[0]["BuyerId"])
            buyer_name = conn.select_query(query)[0]["name"]
            input_massage7_test17["OrderId"] = orders_list_from_table[0]["Id"]
            input_massage7_test17["BuyerName"] = buyer_name
            with RabbitMQ() as mq:
                mq.publish(exchange='eshop_event_bus',
                           routing_key='OrderPaymentFailedIntegrationEvent',
                           body=json.dumps(input_massage7_test17))
            query = "SELECT * from ordering.orders where Id = " + str(input_massage7_test17["OrderId"])
            time.sleep(30)
            canceled_order = conn.select_query(query)[0]
            assert canceled_order["OrderStatusId"] == Cancelled


#####################
#      Test 18      #
#####################
@pytest.mark.ordering_server_respond_when_order_out_of_stock
def test_ordering_server_respond_when_order_out_of_stock(order_api):
    """
    Test 18: Ordering-API server respond accordingly when the order is out of stock
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders where OrderStatusId = 2"
    with MSSQLConnector() as conn:
        orders_list_from_table = conn.select_query(query)
    if len(orders_list_from_table) == 0:
        pytest.skip("No record for execute this test")
    else:
        input_massage3_test18["OrderId"] = orders_list_from_table[0]["Id"]
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockRejectedIntegrationEvent',
                       body=json.dumps(input_massage3_test18))
        query = "SELECT * from ordering.orders where Id = " + str(input_massage3_test18["OrderId"])
        time.sleep(30)
        with MSSQLConnector() as conn:
            canceled_order = conn.select_query(query)[0]
        assert canceled_order["OrderStatusId"] == Cancelled


#####################
#      Test 19      #
#####################
@pytest.mark.ordering_server_respond_when_invalid_order_wrong_price
def test_ordering_server_respond_when_invalid_order_wrong_price(order_api):
    """
    Test 19: Remove invalid order – wrong price
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders"
    with MSSQLConnector() as conn:
        old_length = len(conn.select_query(query))
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key='UserCheckoutAcceptedIntegrationEvent',
                   body=json.dumps(input_massage1_test19))
    time.sleep(10)
    with MSSQLConnector() as conn:
        new_length = len(conn.select_query(query))
        query = "SELECT * FROM ordering.orders WHERE Id = (SELECT max(Id) FROM ordering.orders)"
        for i in range(15):
            time.sleep(5)
            new_order = conn.select_query(query)[0]
            if new_order["OrderStatusId"] == Cancelled:
                break
    assert old_length < new_length
    assert new_order["OrderStatusId"] == Cancelled


#####################
#      Test 20      #
#####################
@pytest.mark.ordering_server_respond_when_invalid_order_wrong_product_id
def test_ordering_server_respond_when_invalid_order_wrong_product_id(order_api):
    """
    Test 20: Remove invalid order – wrong product id
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders"
    with MSSQLConnector() as conn:
        old_length = len(conn.select_query(query))
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key='UserCheckoutAcceptedIntegrationEvent',
                   body=json.dumps(input_massage1_test20))
    time.sleep(10)
    with MSSQLConnector() as conn:
        new_length = len(conn.select_query(query))
        query = "SELECT * FROM ordering.orders WHERE Id = (SELECT max(Id) FROM ordering.orders)"
        for i in range(15):
            time.sleep(5)
            new_order = conn.select_query(query)[0]
            if new_order["OrderStatusId"] == Awaitingvalidation:
                break
    assert old_length < new_length
    assert new_order["OrderStatusId"] == Awaitingvalidation


#####################
#      Test 21      #
#####################
@pytest.mark.ordering_server_ship_order
def test_ordering_server_ship_order(order_api):
    """
    Test 21: Ship order
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders where OrderStatusId = 4"
    with MSSQLConnector() as conn:
        orders_list_from_table = conn.select_query(query)
    if len(orders_list_from_table) == 0:
        pytest.skip("No record for execute this test")
    else:
        assert order_api.ship_order(orders_list_from_table[0]["Id"]).status_code == ok_status_code
        with MSSQLConnector() as conn:
            query = "SELECT * from ordering.orders where id = " + str(orders_list_from_table[0]["Id"])
            new_order_status_id = conn.select_query(query)[0]["OrderStatusId"]
            assert new_order_status_id == Shipped


#####################
#      Test 22      #
#####################
@pytest.mark.ordering_server_ship_order_negative
def test_ordering_server_ship_order_negative(order_api):
    """
    Test 22: Ship order – negative test
    see test case eshop document.
    """
    query = "SELECT * from ordering.orders where OrderStatusId = 1 or OrderStatusId = 2 or " \
            "OrderStatusId = 3 or OrderStatusId = 5 or OrderStatusId = 6"
    with MSSQLConnector() as conn:
        orders_list_from_table = conn.select_query(query)
    if len(orders_list_from_table) == 0:
        pytest.skip("No record for execute this test")
    else:
        old_order_status_id = orders_list_from_table[0]["OrderStatusId"]
        assert order_api.ship_order(orders_list_from_table[0]["Id"]).status_code == bad_status_code
        with MSSQLConnector() as conn:
            query = "SELECT * from ordering.orders where id = " + str(orders_list_from_table[0]["Id"])
            new_order_status_id = conn.select_query(query)[0]["OrderStatusId"]
            assert new_order_status_id == old_order_status_id
