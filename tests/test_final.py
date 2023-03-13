import json
import uuid
import time
from datetime import date

from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *
from utils.ddt import json_read
import pytest

dm = DockerManager()
data = json_read.data_from_json('../utils/ddt/json_file.json')


# @pytest.fixture
# def rabbit_mq():
#     return RabbitMQ()


def start_pre_conditins():
    dm.stop('eshop/basket.api:linux-latest')
    dm.stop('eshop/catalog.api:linux-latest')
    dm.stop('eshop/payment.api:linux-latest')
    dm.stop('eshop/ordering.signalrhub:linux-latest')


def end_pre_conditins():
    dm.start('eshop/basket.api:linux-latest')
    dm.start('eshop/catalog.api:linux-latest')
    dm.start('eshop/payment.api:linux-latest')
    dm.start('eshop/ordering.signalrhub:linux-latest')


def expected_step_1(mq, sql):
    mq.consume('Basket', callback)
    assert check_rk("OrderStartedIntegrationEvent") == True
    mq.consume('Ordering.signalrhub', callback)
    assert check_rk("OrderStatusChangedToSubmittedIntegrationEvent") == True
    mq.consume('Catalog', callback)
    assert check_rk("OrderStatusChangedToAwaitingValidationIntegrationEvent") == True
    mq.consume('Ordering.signalrhub', callback)
    assert check_rk("OrderStatusChangedToAwaitingValidationIntegrationEvent") == True
    time.sleep(10)
    assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0]["OrderStatusId"] == 2


def expected_step_2(mq, sql):
    mq.consume('Ordering.signalrhub', callback)
    assert check_rk("OrderStatusChangedToStockConfirmedIntegrationEvent") == True
    mq.consume('Payment', callback)
    assert check_rk("OrderStatusChangedToStockConfirmedIntegrationEvent") == True
    time.sleep(10)
    assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
               "OrderStatusId"] == 3


def expected_step_3(mq, sql):
        mq.consume('Ordering.signalrhub', callback)
        assert check_rk("OrderStatusChangedToPaidIntegrationEvent") == True
        mq.consume('Catalog', callback)
        assert check_rk("OrderStatusChangedToPaidIntegrationEvent") == True
        time.sleep(10)
        assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                   "OrderStatusId"] == 4


def expected_sql_status(sql, status):
    assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0]["OrderStatusId"] == status


@pytest.mark.test_create_order_MSS
def test_create_order_mss():
    """
    This test check create order - mss
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # step 2
            data[1]["Body"]["OrderId"] = \
            sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            data[1]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[1]["RoutingKey"],
                       body=json.dumps(data[1]["Body"]))
            expected_step_2(mq, sql)
            # step 3
            data[2]["Body"]["OrderId"] = \
            sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            data[2]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[2]["RoutingKey"],
                       body=json.dumps(data[2]["Body"]))
            expected_step_3(mq, sql)
    # end_pre_conditins()


@pytest.mark.test_create_order_with_unavailable_stock
def test_create_order_with_unavailable_stock():
    """
    This test check create order with unavailable stock
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # step 2
            data[3]["Body"]["OrderId"] = \
            sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            data[3]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[3]["RoutingKey"],
                       body=json.dumps(data[3]["Body"]))
            # mq.consume('Ordering.signalrhub', callback)
            # assert check_rk("OrderStockRejectedIntegrationEvent") == True
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "OrderStatusId"] == 6
    # stop_pre_conditins()


@pytest.mark.test_create_order_with_incorrect_payment
def test_create_order_with_incorrect_payment():
    """
    This test check create order with incorrect payment
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # step 2
            data[1]["Body"]["OrderId"] = \
                sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                    "Id"]
            data[1]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[1]["RoutingKey"],
                       body=json.dumps(data[1]["Body"]))
            expected_step_2(mq, sql)
            # step 3
            data[4]["Body"]["OrderId"] = \
            sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            data[4]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[4]["RoutingKey"],
                       body=json.dumps(data[4]["Body"]))
            mq.consume('Ordering.signalrhub', callback)
            assert check_rk("OrderStatusChangedToCancelledIntegrationEvent") == True
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "OrderStatusId"] == 6
    # stop_pre_conditins()


@pytest.mark.test_visa_card_type_id
def test_visa_card_type_id():
    """
    This test check payment when card typy = 2
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardTypeId"] = 2
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_master_card_card_type_id
def test_visa_card_type_id():
    """
    This test check payment when card typy = 3
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardTypeId"] = 3
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_lower_card_type_id
def test_lower_card_type_id():
    """
    This test check payment when card typy = 0
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardTypeId"] = 0
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_upper_card_type_id
def test_upper_card_type_id():
    """
    This test check payment when card typy = 4
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardTypeId"] = 4
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_negative_card_type_id
def test_negative_card_type_id():
    """
    This test check payment when card typy = 0
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardTypeId"] = -1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_expiration_card_past
def test_expiration_card_past():
    """
    This test check payment when expiration card = 2023-03-11
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardExpiration"] = "2023-03-13"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_expiration_card_today
def test_expiration_card_today():
    """
    This test check payment when expiration card = today
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardExpiration"] = str(date.today())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_expiration_card_format_hebrow
def test_expiration_card_format_hebrow():
    """
    This test check payment when expiration card = 12-03-2023
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardExpiration"] = "12-03-2023"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_incorrect_card_number
def test_incorrect_card_number():
    """
    This test check payment when number card = 4012888888881880 instead 4012888888881881
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "4012888888881880"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_short_card_number
def test_short_card_number():
    """
    This test check payment when number card = 401288888888 instead 4012888888881880
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "40128888888"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
    # stop_pre_conditins()


@pytest.mark.test_long_card_number
def test_long_card_number():
    """
    This test check payment when number card = 40128888888818801234 instead 4012888888881880
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "4012888888818801234"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_negative_card_number
def test_negative_card_number():
    """
    This test check payment when number card = -4012888888881881
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "-4012888888881881"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_incorrect_card_holder_name
def test_incorrect_card_holder_name():
    """
    This test check payment when cardholder name = maor
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardHolderName"] = "maor"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_number_card_holder_name
def test_number_card_holder_name():
    """
    This test check payment when cardholder name = 27
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardHolderName"] = "27"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
    # stop_pre_conditins()


@pytest.mark.test_incorrect_card_security_number
def test_incorrect_card_security_number():
    """
    This test check payment when Card Security Number = 534
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardSecurityNumber"] = "534"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_zero_card_security_number
def test_zero_card_security_number():
    """
    This test check payment when Card Security Number = 0
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardSecurityNumber"] = "0"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
            # stop_pre_conditins()


@pytest.mark.test_negative_card_security_number
def test_negative_card_security_number():
    """
    This test check payment when Card Security Number = -533
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardSecurityNumber"] = "-533"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
            # stop_pre_conditins()


@pytest.mark.test_zero_quantity
def test_zero_quantity():
    """
    This test check inventory when quantity = 0
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = 0
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_upper_quantity
def test_upper_quantity():
    """
    This test check inventory when quantity = 1000000000
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = 1000000000
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_negative_quantity
def test_negative_quantity():
    """
    This test check inventory when quantity = -1
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = -1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_zero_product_id
def test_zero_product_id():
    """
    This test check inventory when Product Id = 0
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = 0
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_upper_product_id
def test_upper_product_id():
    """
    This test check inventory when Product Id = 15
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = 15
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_negative_product_id
def test_negative_product_id():
    """
    This test check inventory when Product Id = -1
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = -1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_empty_product_id
def test_empty_product_id():
    """
    This test check inventory when Product Id = ''
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = ''
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_product_id_deleted
def test_product_id_deleted():
    """
    This test check inventory when Product Id deleted
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[5]["Body"]["RequestId"] = str(uuid.uuid4())
            data[5]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[5]["RoutingKey"],
                       body=json.dumps(data[5]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_product_name_error
def test_product_name_error():
    """
    This test check inventory when Product Name ERROR
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[6]["Body"]["RequestId"] = str(uuid.uuid4())
            data[6]["Body"]["Id"] = str(uuid.uuid4())
            data[6]["Body"]["Basket"]["Items"][0]["ProductName"] = "Error"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[6]["RoutingKey"],
                       body=json.dumps(data[6]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_product_name_deleted
def test_product_name_deleted():
    """
    This test check inventory when Product Name deleted
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[7]["Body"]["RequestId"] = str(uuid.uuid4())
            data[7]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[7]["RoutingKey"],
                       body=json.dumps(data[7]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
            # stop_pre_conditins()


@pytest.mark.test_diff_product_name_type
def test_diff_product_name_type():
    """
    This test check inventory when different Product Name type
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductName"] = 1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
            # stop_pre_conditins()


@pytest.mark.test_another_user_name
def test_another_user_name():
    """
    This test check security when another username
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserName"] = "maor@gmail.com"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_another_user_id
def test_another_user_id():
    """
    This test check security when another userid
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserId"] = "55aec9e7-1858-48c2-8b9a-6129a5673e38"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_empy_user_name
def test_empty_user_name():
    """
    This test check security when empty username
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserName"] = ""
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_empty_user_id
def test_empty_user_id():
    """
    This test check security when empty userid
    ----- BUG? -----
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserId"] = ""
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_many_requests_from_basket
def test_many_requests_from_basket():
    """
    This test check scalability when 100 requests from basket
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 101):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_many_requests_from_catalog
def test_many_requests_from_catalog():
    """
    This test check scalability when 100 requests from catalog
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 101):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
            # step 2
            for i in range(1, 101):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_2(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_many_requests_from_payment
def test_many_requests_from_payment():
    """
    This test check scalability when 100 requests from payment
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 101):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
            # step 2
            for i in range(1, 101):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
            # step 3
            for i in range(1, 101):
                data[2]["Body"]["RequestId"] = str(uuid.uuid4())
                data[2]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_3(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_basket_middle
def test_crush_from_basket_middle():
    """
    This test check reliability service create 10 requests from basket and crush in the middle
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                if i == 5:
                    dm.stop('eshop/ordering.api:linux-latest')
                    time.sleep(60)
                expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_catalog_middle
def test_crush_from_catalog_middle():
    """
    This test check reliability service create 10 requests from catalog and crush in the middle
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_1(mq, sql)
            for i in range(1, 11):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
                if i == 5:
                    dm.stop('eshop/ordering.api:linux-latest')
                    time.sleep(60)
                expected_step_2(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_payment_middle
def test_crush_from_payment_middle():
    """
    This test check reliability service create 100 requests from payment and crush in the middle
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_1(mq, sql)
            for i in range(1, 11):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
                expected_step_2(mq, sql)
            for i in range(1, 11):
                data[2]["Body"]["RequestId"] = str(uuid.uuid4())
                data[2]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
                if i == 5:
                    dm.stop('eshop/ordering.api:linux-latest')
                    time.sleep(60)
                expected_step_3(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_basket_start
def test_crush_from_basket_start():
    """
    This test check reliability service create 10 requests from basket and crush in the start
    :param
    """
    dm.stop('eshop/ordering.api:linux-latest')
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
            dm.start('eshop/ordering.api:linux-latest')
            expected_step_1(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_catalog_start
def test_crush_from_catalog_start():
    """
    This test check reliability service create 10 requests from catalog and crush in the middle
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_1(mq, sql)
            dm.stop('eshop/ordering.api:linux-latest')
            for i in range(1, 11):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
            dm.start('eshop/ordering.api:linux-latest')
            expected_step_2(mq, sql)
            # stop_pre_conditins()


@pytest.mark.test_crush_from_payment_start
def test_crush_from_payment_start():
    """
    This test check reliability service create 100 requests from payment and crush in the middle
    :param
    """
    # start_pre_conditins()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            # step 1
            for i in range(1, 11):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
                expected_step_1(mq, sql)
            for i in range(1, 11):
                data[1]["Body"]["RequestId"] = str(uuid.uuid4())
                data[1]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
                expected_step_2(mq, sql)
                dm.stop('eshop/ordering.api:linux-latest')
            for i in range(1, 11):
                data[2]["Body"]["RequestId"] = str(uuid.uuid4())
                data[2]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[1]["RoutingKey"],
                           body=json.dumps(data[1]["Body"]))
            dm.start('eshop/ordering.api:linux-latest')
            expected_step_3(mq, sql)
            # stop_pre_conditins()