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


@pytest.mark.timeout(200)
def test_create_order_when_ordering_service_restarts():
    """
      writer : Artium Brovarnik
      Description: check how ordering cope with new order when the service get restart while in process.
      date: 16.3.23
      """
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    docker = DockerManager()
    docker.restart('eshop/ordering.api:linux-latest')
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

        assert order_status == 4

        mq.consume('Catalog', callback)
        assert global_key() == 'OrderStatusChangedToPaidIntegrationEvent'

        clear_purge()


@pytest.mark.timeout(160)
def test_create_order_when_ordering_service_down():
    """
      writer : Artium Brovarnik
      Description: check how ordering cope with new order  when the service is shut down while in process.
      date: 16.3.23
      """
    docker = DockerManager()
    try:
        docker.stop('eshop/ordering.api:linux-latest')
        inputs = Inputs()
        inputs.create_new_order()
        order_status = None
        with RabbitMQ() as mq:
            docker.start('eshop/ordering.api:linux-latest')
            time.sleep(5)
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
    finally:
        docker.start('eshop/ordering.api:linux-latest')
        clear_purge()

@pytest.mark.timeout(160)
def test_create_100_new_orders():
    """
      writer : Artium Brovarnik
      Description: check how ordering cope with 100 new orders request
      date: 16.3.23
      """
    docker = DockerManager()
    inputs = Inputs()
    count_of_rows_before = get_order_count()
    try:
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        for i in range(10):
            inputs.create_new_order()
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        time.sleep(5)
        count_of_rows_after = get_order_count()
        assert count_of_rows_before[0][''] + 10 == count_of_rows_after[0]['']
    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()

