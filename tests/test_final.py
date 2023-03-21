import json
import uuid
import time
from datetime import date

from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_receive import *
from utils.ddt import json_read
import pytest

dm = DockerManager()
data = json_read.data_from_json('../utils/ddt/json_file.json')


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


def start_containers():
    dm.start('eshop/basket.api:linux-latest')
    dm.start('eshop/catalog.api:linux-latest')
    dm.start('eshop/payment.api:linux-latest')
    dm.start('eshop/ordering.signalrhub:linux-latest')


@pytest.fixture
def stop_containers():
    dm.stop('eshop/basket.api:linux-latest')
    dm.stop('eshop/catalog.api:linux-latest')
    dm.stop('eshop/payment.api:linux-latest')
    dm.stop('eshop/ordering.signalrhub:linux-latest')


@pytest.fixture
def queues_clone():
    with RabbitMQ() as mq:
        mq.channel.queue_purge("Basket")
        mq.channel.queue_purge("Catalog")
        mq.channel.queue_purge("Payment")
        mq.channel.queue_purge("Ordering.signalrhub")


@pytest.mark.requirement1
def test_create_order_mss(queues_clone):
    """
    This test check create order - mss
    :param
    """
    dm.stop('eshop/basket.api:linux-latest')
    dm.stop('eshop/catalog.api:linux-latest')
    dm.stop('eshop/payment.api:linux-latest')
    dm.stop('eshop/ordering.signalrhub:linux-latest')
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
            start_containers()


@pytest.mark.requirement1
def test_create_order_with_unavailable_stock(stop_containers, queues_clone):
    """
    This test check create order with unavailable stock
    :param
    """
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
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "OrderStatusId"] == 6


@pytest.mark.requirement1
def test_create_order_with_incorrect_payment(stop_containers, queues_clone):
    """
    This test check create order with incorrect payment
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "OrderStatusId"] == 6


@pytest.mark.other
def test_visa_card_type_id(stop_containers, queues_clone):
    """
    This test check payment when card typy = 2
    :param
    """
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
            start_containers()


@pytest.mark.requirement3
def test_master_card_card_type_id(stop_containers, queues_clone):
    """
    This test check payment when card typy = 3
    :param
    """
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
            start_containers()


@pytest.mark.requirement3
def test_lower_card_type_id(stop_containers, queues_clone):
    """
    This test check payment when card typy = 0
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_upper_card_type_id(stop_containers, queues_clone):
    """
    This test check payment when card typy = 4
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_negative_card_type_id(stop_containers, queues_clone):
    """
    This test check payment when card typy = -1
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_expiration_card_past(stop_containers, queues_clone):
    """
    This test check payment when expiration card = 2023-03-11
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_expiration_card_today(stop_containers, queues_clone):
    """
    This test check payment when expiration card = today
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_expiration_card_format_hebrew(stop_containers, queues_clone):
    """
    This test check payment when expiration card = 12-03-2023
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_short_card_number(stop_containers, queues_clone):
    """
    This test check payment when number card = 401288888888 instead 4012888888881880
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_zero_card_security_number(stop_containers, queues_clone):
    """
    This test check payment when Card Security Number = 0
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement3
def test_negative_card_security_number(stop_containers, queues_clone):
    """
    This test check payment when Card Security Number = -533
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_product_name_deleted(stop_containers, queues_clone):
    """
    This test check inventory when Product Name deleted
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_diff_product_name_type(stop_containers, queues_clone):
    """
    This test check inventory when different Product Name type
    :param
    """
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
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement6
def test_many_requests(stop_containers, queues_clone):
    """
    This test check scalability when 100 requests
    check - from last line (before 100 requests) if I have 100 lines on sql with status id = 4 in hour
    :param
    """
    start_containers()
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_id = sql.req_query('SELECT top 1 Id from ordering.orders ORDER BY Id DESC')[0]['Id']
            print(last_id)
            # step 1
            for i in range(1, 101):
                data[0]["Body"]["RequestId"] = str(uuid.uuid4())
                data[0]["Body"]["Id"] = str(uuid.uuid4())
                mq.publish(exchange='eshop_event_bus',
                           routing_key=data[0]["RoutingKey"],
                           body=json.dumps(data[0]["Body"]))
            while True:
                start_time = time.time()
                if time.time() - start_time > 360:
                    if time.time() - start_time > 3600 or sql.req_query(f'SELECT amount from (SELECT count(Id) as '
                                                                        f'amount, OrderStatusId from ordering.orders '
                                                                        f'where Id > ({last_id}) GROUP BY '
                                                                        f'OrderStatusId) o where OrderStatusId = 4')[
                                                                        0]['amount'] == 100:
                        end_time = time.time()
                        print(end_time - start_time)
                        assert sql.req_query(f'SELECT amount from (SELECT count(Id) as amount, OrderStatusId from '
                                             f'ordering.orders where Id > ({last_id}) GROUP BY OrderStatusId) o where'
                                             f' OrderStatusId = 4')[0]['amount'] == 100
                        break
                time.sleep(1)


@pytest.mark.requirement3
def test_incorrect_card_number(stop_containers, queues_clone):
    """
    This test check payment when number card = 4012888888881880 instead 4012888888881881
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement3
def test_long_card_number(stop_containers, queues_clone):
    """
    This test check payment when number card = 4012888888881880123 instead 4012888888881880
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "4012888888818801234"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement3
def test_negative_card_number(stop_containers, queues_clone):
    """
    This test check payment when number card = -4012888888881881
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardNumber"] = "-4012888888881881"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement3
def test_incorrect_card_holder_name(stop_containers, queues_clone):
    """
    This test check payment when cardholder name = maor
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardHolderName"] = "maor"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement3
def test_number_card_holder_name(stop_containers, queues_clone):
    """
    This test check payment when cardholder name = 27
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardHolderName"] = "27"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement3
def test_incorrect_card_security_number(stop_containers, queues_clone):
    """
    This test check payment when Card Security Number = 534
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["CardSecurityNumber"] = "534"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] != last_order


@pytest.mark.requirement4
def test_zero_quantity(stop_containers, queues_clone):
    """
    This test check inventory when quantity = 0
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = 0
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_upper_quantity(stop_containers, queues_clone):
    """
    This test check inventory when quantity = 1000000000
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = 1000000000
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_negative_quantity(stop_containers, queues_clone):
    """
    This test check inventory when quantity = -1
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["Quantity"] = -1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_zero_product_id(stop_containers, queues_clone):
    """
    This test check inventory when Product Id = 0
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = 0
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_upper_product_id(stop_containers, queues_clone):
    """
    This test check inventory when Product Id = 15
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = 15
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_negative_product_id(stop_containers, queues_clone):
    """
    This test check inventory when Product Id = -1
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = -1
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_empty_product_id(stop_containers, queues_clone):
    """
    This test check inventory when Product Id = ''
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["Basket"]["Items"][0]["ProductId"] = ''
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_product_id_deleted(stop_containers, queues_clone):
    """
    This test check inventory when Product Id deleted
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[5]["Body"]["RequestId"] = str(uuid.uuid4())
            data[5]["Body"]["Id"] = str(uuid.uuid4())
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[5]["RoutingKey"],
                       body=json.dumps(data[5]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement4
def test_product_name_error(stop_containers, queues_clone):
    """
    This test check inventory when Product Name ERROR
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[6]["Body"]["RequestId"] = str(uuid.uuid4())
            data[6]["Body"]["Id"] = str(uuid.uuid4())
            data[6]["Body"]["Basket"]["Items"][0]["ProductName"] = "Error"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[6]["RoutingKey"],
                       body=json.dumps(data[6]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement5
def test_another_user_name(stop_containers, queues_clone):
    """
    This test check security when another username
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserName"] = "maor@gmail.com"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement5
def test_another_user_id(stop_containers, queues_clone):
    """
    This test check security when another userid
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserId"] = "55aec9e7-1858-48c2-8b9a-6129a5673e38"
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement5
def test_empty_user_name(stop_containers, queues_clone):
    """
    This test check security when empty username
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserName"] = ""
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order


@pytest.mark.requirement5
def test_empty_user_id(stop_containers, queues_clone):
    """
    This test check security when empty userid
    ----- BUG? -----
    :param
    """
    with RabbitMQ() as mq:
        with MSSQLConnector() as sql:
            last_order = sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                "Id"]
            # step 1
            data[0]["Body"]["RequestId"] = str(uuid.uuid4())
            data[0]["Body"]["Id"] = str(uuid.uuid4())
            data[0]["Body"]["UserId"] = ""
            mq.publish(exchange='eshop_event_bus',
                       routing_key=data[0]["RoutingKey"],
                       body=json.dumps(data[0]["Body"]))
            time.sleep(15)
            start_containers()
            assert sql.req_query("SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC")[0][
                       "Id"] == last_order
