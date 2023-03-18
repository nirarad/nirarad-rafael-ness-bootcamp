import pytest
import pytest_timeout
import json
import os
from utils.api.bearer_tokenizer import BearerTokenizer
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *
from utils.rabbitmq.inputs import Inputs
import uuid
from utils.db import db_utils
import time
from utils.docker.docker_utils import DockerManager

def clear_purge():
    """
    Author: Artium Brovarnik
    Description: clear queues from messages
    date 16.3.23
    """
    with RabbitMQ() as mq:
        mq.clear_queues('Basket')
        mq.clear_queues('Catalog')
        mq.clear_queues('Payment')
def get_id_of_last_order():
    """
    Author: Artium Brovarnik
    Description: get from orders.ordering table the max id
    date 16.3.23
    """
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT top(1) oo.id from ordering.orders as oo order by id desc')
def get_order_count():
    """
    Author: Artium Brovarnik
    Description: get from orders.ordering count of all orders
    date 16.3.23
    """
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT count(oo.id) from ordering.orders as oo ')
def get_status_of_last_order():
    """
    Author: Artium Brovarnik
    Description: get from orders.ordering orderStatusID from  the max id
    date 16.3.23
    """
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT top(1) oo.orderstatusid from ordering.orders as oo order by id desc')



def test_order_response():
    """
   writer : Artium Brovarnik
   Description: check response -  status code from get orders - smoke
   date: 16.3.23
   """
    api = OrderingAPI()
    orders = api.get_orders()
    assert orders.status_code==200

@pytest.mark.timeout(200)
def test_create_order_successfully():
    """
    Author: Artium Brovarnik
    Description: Check creating a new order successfully
    date 17.3.23
    """
    inputs = Inputs()
    # step 1
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == 'OrderStartedIntegrationEvent'

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']

        # Wait for the order status to change to 2
        while order_status != 2:
            time.sleep(1)
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == 2

        mq.consume('Catalog', callback)
        assert global_key() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

        # step2
        inputs.catalog_confirm(order_id)

        while order_status != 3:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == 3

        mq.consume('Payment', callback)
        assert global_key() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'

        # step3
        inputs.payment_confirm(order_id)

        while order_status != 4:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == 4

        mq.consume('Catalog', callback)
        assert global_key() == 'OrderStatusChangedToPaidIntegrationEvent'

        clear_purge()


@pytest.mark.timeout(200)
def test_response_cancel_action():
    """
   writer : Artium Brovarnik
   Description: check status code from delete action (from status 2)
   date: 16.3.23
   """
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == 'OrderStartedIntegrationEvent'

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        while order_status != 2:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == 2

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))

        clear_purge()

@pytest.mark.timeout(200)
def test_update_order():
    """
   writer : Artium Brovarnik
   Description: check update order status payment (4) to status shipped (5) , should success
   date: 16.3.23
   """
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == 'OrderStartedIntegrationEvent'

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        while order_status != 2:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == 2

        mq.consume('Catalog', callback)
        assert global_key() == 'OrderStatusChangedToAwaitingValidationIntegrationEvent'

        inputs.catalog_confirm(order_id)

        while order_status != 3:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == 3

        mq.consume('Payment', callback)
        assert global_key() == 'OrderStatusChangedToStockConfirmedIntegrationEvent'
        inputs.payment_confirm(order_id)

        while order_status != 4:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == 4

        mq.consume('Catalog', callback)
        assert global_key() == 'OrderStatusChangedToPaidIntegrationEvent'

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'shipped'
        clear_purge()



