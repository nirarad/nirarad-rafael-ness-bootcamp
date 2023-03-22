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
from utils.db import *


# queries for use in tests
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


@pytest.mark.timeout(160)
def test_create_order_successfully():
    """
    Author: Artium Brovarnik
    Description: Check for the process of ordering a new order successfully
    date 17.3.23
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        # step 3
        inputs.payment_confirm(order_id)
        while order_status != int(os.getenv('ID_FOUR')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == int(os.getenv('ID_FOUR'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('ORDER_TO_CATALOG_END')

        clear_purge()

@pytest.mark.timeout(120)
def test_create_order_with_out_stock():
    """
    writer : Artium Brovarnik
    Description: check creating order when items out of stock
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_reject(order_id)
        while order_status != 6:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
            # Assert that the order status is 6
        assert order_status == int(os.getenv('ID_SIX'))
        clear_purge()

@pytest.mark.timeout(140)
def test_create_order_payment_rejected():
    """
    writer : Artium Brovarnik
    Description: creating order  when the payment process failed.
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')


        inputs.payment_reject(order_id)
        while order_status != 6:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
            # Assert that the order status is 6
        assert order_status == int(os.getenv('ID_SIX'))

        clear_purge()

# @pytest.mark.skip(reason="problem with reporter")
def test_update_from_status_1():
    """
    writer : Artium Brovarnik
    Description: check update order status from submmited (1) to  shipped (5)
    date: 16.3.23
    """
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))

        docker = DockerManager()
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)
            assert global_key() == os.getenv('order_to_basket')

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('id_one'))
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']

            api = OrderingAPI()
            result_api = api.update_statusId_to_shipped(order_id)
            assert result_api.status_code == int(os.getenv('BAD'))
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('ID_ONE'))


            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == int(os.getenv('OK'))
            assert api_get_order_by_id.json()['status'] == os.getenv('submitted')


        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()

@pytest.mark.timeout(150)
def test_update_from_status_2():
    """
    writer : Artium Brovarnik
    Description: check update order status Awaitingvalidation (2) to status shipped (5)
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')


        api = OrderingAPI()
        results_api = api.update_statusId_to_shipped(order_id)
        assert results_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_TWO'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('AWAITING')

        clear_purge()

@pytest.mark.timeout(160)
def test_update_from_status_3():
    """
   writer : Artium Brovarnik
   Description: check update order status Stockconfirmed (3) to status shipped (5)
   date: 16.3.23
   """
    # step 1
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_THREE'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('stockconfirm')

        clear_purge()

@pytest.mark.timeout(160)
def test_update_from_status_4():
    """
  writer : Artium Brovarnik
  Description: check update order status payment (4) to status shipped (5)
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        # step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        # step 3
        inputs.payment_confirm(order_id)
        while order_status != int(os.getenv('ID_FOUR')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == int(os.getenv('ID_FOUR'))

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('id_five'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('shipped')

        clear_purge()

@pytest.mark.timeout(160)
def test_update_from_status_6():
    """
   writer : Artium Brovarnik
   Description: check the update from status Cancelled 6 to Shipped 5
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        api = OrderingAPI()
        api.update_statusId_to_cancelled(order_id)
        assert api.update_statusId_to_cancelled(order_id).status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('id_six'))

        api.update_statusId_to_shipped(order_id)
        assert api.update_statusId_to_shipped(order_id).status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('id_six'))

        clear_purge()

@pytest.mark.timeout(160)
def test_cancel_from_status_1():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status submmited (1) to status cancelled (6)
   date: 16.3.23
   """
    docker = DockerManager()
    inputs = Inputs()
    inputs.create_new_order()
    try:

        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)
            assert global_key() == os.getenv('order_to_basket')

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('id_one'))
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']

            api = OrderingAPI()
            update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
            assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == int(os.getenv('id_six'))

            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == int(os.getenv('OK'))
            assert api_get_order_by_id.json()['status'] == os.getenv('cancelled')
    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()

@pytest.mark.timeout(150)
def test_cancel_from_status_2():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status Awaitingvalidation (2) to status cancelled (6)
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_SIX'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('CANCELLED')

        clear_purge()

@pytest.mark.timeout(150)
def test_cancel_from_status_3():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status Stockconfirmed (3) to status cancelled (6)
   date: 16.3.23
   """
    #step 1
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        #step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_SIX'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('CANCELLED')

        clear_purge()

@pytest.mark.timeout(150)
def test_cancel_from_status_4():
    """
      writer : Artium Brovarnik
      Description: check cancel order status from payment (4) to status cancelled (6)
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        #step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        #step 3
        inputs.payment_confirm(order_id)
        while order_status != int(os.getenv('ID_FOUR')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == int(os.getenv('ID_FOUR'))

        # cancel
        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_FOUR'))

        #get by id
        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('PAID')

        clear_purge()


@pytest.mark.timeout(150)
def test_cancel_from_status_5():
    """
      writer : Artium Brovarnik
      Description: check cancel order status from Shipped (5) to status cancelled (6)
      date: 16.3.23
      """
    # step 1
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
        while order_status != int(os.getenv('ID_TWO')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 2
        assert order_status == int(os.getenv('ID_TWO'))

        mq.consume('Catalog', callback)
        assert global_key() == os.getenv('order_to_catalog')

        #step 2
        inputs = Inputs()
        inputs.catalog_confirm(order_id)
        while order_status != int(os.getenv('ID_THREE')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == int(os.getenv('ID_THREE'))

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        #step 3
        inputs.payment_confirm(order_id)
        while order_status != int(os.getenv('ID_FOUR')):
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == int(os.getenv('ID_FOUR'))

        api = OrderingAPI()
        api.update_statusId_to_shipped(order_id)
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_FIVE'))

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == int(os.getenv('ID_FIVE'))

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == os.getenv('SHIPPED')

        clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_with_cardTypeId_only_chars():
    """
    writer : Artium Brovarnik
    Description: check create new order when CardTypeId included only chars
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["CardTypeId"] = 'error'
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_order_when_cardTypeId_not_exsists():
    """
     writer : Artium Brovarnik
     Description: check create new order when Cardtype Id  is not exsists in ordering.cardTypes table
     date: 16.3.23
     """
    len_of_the_orders_before = get_order_count()
    create_order["CardTypeId"] = 29
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_order_when_user_not_exist_in_db():
    """
    writer : Artium Brovarnik
    Description: check if order created when user not exist in db identityDB aspNetUsers table - should fail.
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["UserName"] = "error"
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_when_card_secuirtyNumber_only_chars():
    """
   writer : Artium Brovarnik
   Description: check create new order when CardSecurityNumber included only chars
   date: 16.3.23
   """
    len_of_the_orders_before = get_order_count()
    create_order["CardSecurityNumber"] = 'error'
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_card_number_only_chars():
    """
     writer : Artium Brovarnik
     Description: check if order created when cardNumber included only chars
     date: 16.3.23
     """
    len_of_the_orders_before = get_order_count()
    create_order["CardNumber"] = "error"
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_order_when_there_is_no_zipcode():
    """
  writer : Artium Brovarnik
  Description: check when creating order with not a zipcode
  date: 16.3.23
  """
    len_of_the_orders_before = get_order_count()
    create_order["ZipCode"] = ""
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_new_order_card_expired():
    """
    writer : Artium Brovarnik
    Description: check creating order when card expired
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["CardExpiration"] = "2010-10-31T22:00:00Z"
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_with_negative_items_quantity():
    """
      writer : Artium Brovarnik
      Description: check when creating order with a negative number of items
      date: 16.3.23
      """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["Quantity"] = -5
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_new_order_with_zero_items():
    """
      writer : Artium Brovarnik
      Description: check when creating order with  zero items
      date: 16.3.23
      """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["Quantity"] = 0
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_with_productId_not_exist():
    """
     writer : Artium Brovarnik
     Description: check when creating order with a product id that doesn't  exist in the db catalog.catalogDb table.
     date: 16.3.23
     """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["ProductId"] = 999
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_with_productId_only_chars():
    """
    writer : Artium Brovarnik
    Description: : check when creating order with a product id included only chars.
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["ProductId"] = 'error'
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_new_order_with_negative_price():
    """
    writer : Artium Brovarnik
    Description: : : check when creating order with a price of item with negative numbers.
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["UnitPrice"] = -19.5
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_with_negative_productId():
    """
    writer : Artium Brovarnik
    Description: : check when creating order with a product id with  negative numbers.
    date: 16.3.23
    """
    len_of_the_orders_before = get_order_count()
    create_order["Basket"]["Items"][0]["ProductId"] = -2
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus', routing_key=os.getenv('BASKET_TO_ORDER'),
                   body=json.dumps(create_order))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    pprint.pprint(create_order)
    clear_purge()




























