import pprint
import pytest
import pytest_timeout
import json
import os
from utils.api.bearer_tokenizer import BearerTokenizer
from dotenv import load_dotenv
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *
from utils.rabbitmq.inputs import Inputs
from utils.db import db_utils
import time
from utils.docker.docker_utils import DockerManager
import os
load_dotenv()
from utils.rabbitmq.rabbitmq_send import RabbitMQ
import uuid
from utils.rabbitmq.inputs import  *
from tests.test_functional import *





@pytest.mark.timeout(160)
def test_cancel_order_from_another_user():
    """
      writer : Artium Brovarnik
      Description: check cancelling order from another user
      date: 16.3.23
    """
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == os.getenv('ORDER_TO_BASKET')

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        wait_to_status(2)

    another_user = OrderingAPI('bob','Pass123$')
    cancel_order = another_user.update_statusId_to_cancelled(order_id)
    assert cancel_order.status_code == int(os.getenv('BAD'))

    clear_purge()

@pytest.mark.timeout(160)
def test_update_order_from_another_user():
    """
      writer : Artium Brovarnik
      Description: check update order from another user
      date: 16.3.23
    """
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == os.getenv('order_to_basket')

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        wait_to_status(2)

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        wait_to_status(3)

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        # step 3
        inputs.payment_confirm(order_id)
        wait_to_status(4)

        another_user = OrderingAPI('bob', 'Pass123$')
        update_order = another_user.update_statusId_to_cancelled(order_id)
        assert update_order.status_code == int(os.getenv('BAD'))
        clear_purge()

@pytest.mark.timeout(160)
def test_get_order_by_another_user():
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == os.getenv('ORDER_TO_BASKET')

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        wait_to_status(2)


    another_user = OrderingAPI('bob','Pass123$')
    get_order = another_user.get_order_by_id(order_id)
    assert get_order.status_code == int(os.getenv('BAD'))

    clear_purge()

@pytest.mark.skip(reason="problem with reporter")
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
            time.sleep(7)
            mq.consume('Basket', callback)
            assert global_key() == os.getenv('order_to_basket')

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']
            # Wait for the order status to change to 2
            wait_to_status(2)
            mq.consume('Catalog', callback)
            assert global_key() == os.getenv('order_to_catalog')

            inputs.catalog_confirm(order_id)

            wait_to_status(3)
            mq.consume('Payment', callback)
            assert global_key() == os.getenv('ORDER_TO_PAYMENT')
            inputs.payment_confirm(order_id)

            wait_to_status(4)

            mq.consume('Catalog', callback)
            assert global_key() == os.getenv('ORDER_TO_CATALOG_END')
    finally:
        docker.start('eshop/ordering.api:linux-latest')
        clear_purge()

@pytest.mark.timeout(160)
def test_create_100_new_orders_in_queue():
    """
      writer : Artium Brovarnik
      Description: check how ordering service cope with 100 messages in queue
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

@pytest.mark.timeout(200)
def test_create_order_when_ordering_service_restarts():
    """
      writer : Artium Brovarnik
      Description: check how ordering cope with new order when the service get restart while in process.
      date: 16.3.23
      """
    # step1
    inputs = Inputs()
    inputs.create_new_order()
    order_status = None
    docker = DockerManager()
    docker.restart('eshop/ordering.api:linux-latest')
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == os.getenv('order_to_basket')

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
        order_id_query = get_id_of_last_order()
        order_id = order_id_query[0]['id']
        # Wait for the order status to change to 2
        wait_to_status(2)

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step2
        inputs.catalog_confirm(order_id)
        wait_to_status(3)
        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        # step3
        inputs.payment_confirm(order_id)
        wait_to_status(4)
        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('ORDER_TO_CATALOG_END')

        clear_purge()

def test_create_100_new_orders_per_hour():
    """
      writer : Artium Brovarnik
      Description: check how ordering cope with 100 new orders request
      date: 16.3.23
      """
    # step1
    inputs = Inputs()
    count_of_rows_before = get_order_count()
    start_time = time.time()
    for i in range(10):
        inputs.create_new_order()
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)
            assert global_key() == os.getenv('order_to_basket')

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']
            # Wait for the order status to change to 2
            wait_to_status(2)

            mq.consume('Catalog', callback)
            assert global_key() == os.getenv('order_to_catalog')

            # step 2
            inputs = Inputs()
            inputs.catalog_confirm(order_id)
            wait_to_status(3)

            mq.consume('Payment', callback)
            assert global_key() == os.getenv('ORDER_TO_PAYMENT')

            # step 3
            inputs.payment_confirm(order_id)
            wait_to_status(4)

            mq.consume('Catalog', callback)
            assert global_key() == os.getenv('ORDER_TO_CATALOG_END')

    count_of_rows_after = get_order_count()
    end_time = time.time()
    total_time = end_time - start_time
    assert  total_time<=3600
    assert count_of_rows_before[0][''] + 10 == count_of_rows_after[0]['']

    clear_purge()
