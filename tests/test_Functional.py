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
import uuid
from utils.db import db_utils
import time
from utils.docker.docker_utils import DockerManager
import os
load_dotenv()
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


@pytest.mark.timeout(160)
def test_create_order_successfully():
    """
    Author: Artium Brovarnik
    Description: Check for the process of ordering a new order successfully
    date 17.3.23
    """
    inputs = Inputs()
    # step 1
    inputs.create_new_order()
    order_status = None
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)
        assert global_key() == os.getenv('ORDER_TO_BASKET')

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
        assert global_key() == os.getenv('ORDER_TO_CATALOG')

        #step2
        inputs.catalog_confirm(order_id)

        while order_status != 3:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 3
        assert order_status == 3

        mq.consume('Payment', callback)
        assert global_key() == os.getenv('ORDER_TO_PAYMENT')

        #step3
        inputs.payment_confirm(order_id)

        while order_status != 4:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
        # Assert that the order status is 4
        assert order_status == 4

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
    inputs.create_new_order_out_of_stock()
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

        inputs.catalog_reject(order_id)

        while order_status != 6:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
            # Assert that the order status is 6
        assert order_status == 6

        clear_purge()

@pytest.mark.timeout(120)
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

        inputs.payment_reject(order_id)
        while order_status != 6:
            time.sleep(1)  # Wait for 1 second before checking the status again
            results = get_status_of_last_order()
            order_status = results[0]['orderstatusid']
            # Assert that the order status is 6
        assert order_status == 6

        clear_purge()

#update tests
@pytest.mark.timeout(120)
def test_update_from_status_1():
    """
    writer : Artium Brovarnik
    Description: check update order status from submmited (1) to  shipped (5) , should fail
    date: 16.3.23
    """
    docker = DockerManager()
    inputs = Inputs()
    inputs.create_new_order()
    try:
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:

            mq.consume('Basket', callback)
            assert global_key() == 'OrderStartedIntegrationEvent'

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']

            api = OrderingAPI()
            result_api = api.update_statusId_to_shipped(order_id)
            assert result_api.status_code == int(os.getenv('BAD'))
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == int(os.getenv('OK'))
            assert api_get_order_by_id.json()['status'] == 'submitted'
    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        # clear_purge()

@pytest.mark.timeout(120)
def test_update_from_status_2():
    """
    writer : Artium Brovarnik
    Description: check update order status Awaitingvalidation (2) to status shipped (5) ,should fail
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

        api = OrderingAPI()
        results_api = api.update_statusId_to_shipped(order_id)
        assert results_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 2

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'awaitingvalidation'

        clear_purge()

@pytest.mark.timeout(160)
def test_update_from_status_3():
    """
   writer : Artium Brovarnik
   Description: check update order status Stockconfirmed (3) to status shipped (5) ,should fail.
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

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == int(os.getenv('BAD'))

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 3

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'stockconfirmed'

        clear_purge()


@pytest.mark.timeout(160)
def test_update_from_status_4():
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


@pytest.mark.timeout(160)
def test_update_from_status_6():
    """
   writer : Artium Brovarnik
   Description: check the update from status Cancelled 6 to Shipped 5 , should fail
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

        api = OrderingAPI()
        api.update_statusId_to_cancelled(order_id)
        assert api.update_statusId_to_cancelled(order_id).status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api = OrderingAPI()
        api.update_statusId_to_shipped(order_id)
        assert api.update_statusId_to_shipped(order_id).status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        clear_purge()

#cancel tests
@pytest.mark.timeout(120)
def test_cancel_from_status_1():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status submmited (1) to status cancelled (6) , should canceled
   date: 16.3.23
   """
    docker = DockerManager()
    inputs = Inputs()
    inputs.create_new_order()
    try:
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)
            assert global_key() == 'OrderStartedIntegrationEvent'

            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1
            order_id_query = get_id_of_last_order()
            order_id = order_id_query[0]['id']

            api = OrderingAPI()
            update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
            assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 6

            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == int(os.getenv('OK'))
            assert api_get_order_by_id.json()['status'] == 'cancelled'

    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()


@pytest.mark.timeout(120)
def test_cancel_from_status_2():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status Awaitingvalidation (2) to status cancelled (6) , should canceled
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

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'cancelled'

        clear_purge()


@pytest.mark.timeout(120)
def test_cancel_from_status_3():
    """
   writer : Artium Brovarnik
   Description: check cancel order from status Stockconfirmed (3) to status cancelled (6) , should canceled
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

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('OK'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'cancelled'

        clear_purge()


@pytest.mark.timeout(120)
def test_cancel_from_status_4():
    """
      writer : Artium Brovarnik
      Description: check cancel order status from payment (4) to status cancelled (6) , should fail
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

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 4

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'paid'

        clear_purge()


@pytest.mark.timeout(120)
def test_cancel_from_status_5():
    """
      writer : Artium Brovarnik
      Description: check cancel order status from Shipped (5) to status cancelled (6) , should fail
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

        api = OrderingAPI()
        api.update_statusId_to_shipped(order_id)
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == int(os.getenv('BAD'))
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == int(os.getenv('OK'))
        assert api_get_order_by_id.json()['status'] == 'shipped'

        clear_purge()


@pytest.mark.timeout(120)
def test_create_order_when_user_not_exist_in_db():
    """
    writer : Artium Brovarnik
    Description: check if order created when user not exist in db identityDB aspNetUsers table - should fail.
    date: 16.3.23
    """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_order_when_user_not_exist_in_db()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

    clear_purge()

@pytest.mark.timeout(120)
def test_create_order_when_there_is_no_zipcode():
    """
  writer : Artium Brovarnik
  Description: check when creating order with a zipcode icluded only chars
  date: 16.3.23
  """
    inputs = Inputs()
    count_of_the_orders_before = get_order_count()
    inputs.create_order_without_zipcode()
    count_of_the_orders_after = get_order_count()
    assert count_of_the_orders_before[0][''] == count_of_the_orders_after[0]['']

    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_card_number_only_chars():
    """
     writer : Artium Brovarnik
     Description: check if order created when cardNumber included only chars
     date: 16.3.23
     """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_new_order_card_number_only_chars()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

    clear_purge()

@pytest.mark.timeout(120)
def test_create_order_when_cardTypeId_not_defind():
    """
     writer : Artium Brovarnik
     Description: check create new order when CardTypeId  number not defined in ordering.cardTypes table
     should not create new order in db.
     date: 16.3.23
     """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_order_when_cardTypeId_not_defind()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()


@pytest.mark.timeout(120)
def test_create_new_order_card_expired():
    """
    writer : Artium Brovarnik
    Description: check creating order when card expired
    should not create new order.
    date: 16.3.23
    """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_new_order_card_expired()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_when_CardTypeId_only_chars():
    """
    writer : Artium Brovarnik
    Description: check create new order when CardTypeId included only chars
    date: 16.3.23
    """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_new_order_when_CardTypeId_only_chars()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

    clear_purge()

@pytest.mark.timeout(120)
def test_create_new_order_when_CardSecuirtyNumber_only_chars():
    """
   writer : Artium Brovarnik
   Description: check create new order when CardSecurityNumber included only chars
   date: 16.3.23
   """
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_new_order_when_CardSecuirtyNumber_only_chars()
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

    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_new_order_with_negative_items_quantity()
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
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.create_new_order_with_zero_items()
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
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_new_order_with_productId_not_exist()
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
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_new_order_with_productId_only_chars()
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
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_new_order_with_negative_productId()
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
    inputs = Inputs()
    len_of_the_orders_before = get_order_count()
    inputs.test_create_new_order_with_negative_price()
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']
    clear_purge()