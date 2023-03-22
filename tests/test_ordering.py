import pytest
import os
from dotenv import load_dotenv
from utils.api.ordering_api import OrderingAPI
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.rabbitmq.rabbitmq_receive import *
from utils.rabbitmq.message import Message
from utils.db import db_utils
import time
from utils.docker.docker_utils import DockerManager

load_dotenv()


def clear_purge():
    with RabbitMQ() as mq:
        mq.clear_queues('Basket')
        mq.clear_queues('Catalog')
        mq.clear_queues('Payment')
def get_id_of_last_order():
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT top(1) oo.id from ordering.orders as oo order by id desc')
def get_order_count():
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT count(oo.id) from ordering.orders as oo ')
def get_status_of_last_order():
    with MSSQLConnector() as conn:
        return conn.select_query('SELECT top(1) oo.orderstatusid from ordering.orders as oo order by id desc')
def wait_for_order_status(order_status_id):
    while True:
        time.sleep(1)
        results = get_status_of_last_order()
        if results[0]['orderstatusid'] == order_status_id:
            break









@pytest.mark.functional
def test_create_order_successfully_mss():
    """
    Author: Daniel.A
    Description: Test that an order is created successfully when there are items in stock and payment is successful.
    """
    message = Message()
    message.order_data()
    # Create a new order and verify that it has started processing
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

@pytest.mark.functional
def test_create_order_with_out_stock():
    """
    Author name :Daniel.A
    Description: check creating order when items out of stock .
    date:
    """
    message = Message()
    message.order_data(quantity=1000)
    # Create a new order and verify that it has started processing
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_Rejected(order_id)

        # Wait for the order status to change to 'cancelled'
        wait_for_order_status(6)

@pytest.mark.functional
def test_create_order_payment_rejected():
    """
    Author name :Daniel.A
    Description: creating order successfully when there is items in stock and payment failed.
    date:
    """
    message = Message()
    message.order_data()
    order_status = None
    # Create a new order and verify that it has started processing
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_rejected(order_id)

        # Wait for the order status to change to 'cancelled'
        wait_for_order_status(6)

@pytest.mark.functional
def test_update_from_1_to_5_should_not_update():
    """
    Author name :Daniel.A
    Description: check update order status submitted (1) to status shipped (5) should fail.
    date:
    """
    docker = DockerManager()
    message = Message()
    message.order_data()
    try:
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)

            # Verify that the order status is 'created'
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            # Retrieve the ID of the last created order
            order_id = get_id_of_last_order()[0]['id']

            api = OrderingAPI()
            result_api = api.update_statusId_to_shipped(order_id)
            assert result_api.status_code == 400
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == 200
            assert api_get_order_by_id.json()['status'] == 'submitted'
    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()

@pytest.mark.functional
def test_update_from_2_to_5_should_not_update():
    """
    Author name :Daniel.A
    Description: check update order status AwaitingValidation (2) to status shipped (5) should fail.
    date:
    """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')

        api = OrderingAPI()
        results_api = api.update_statusId_to_shipped(order_id)
        assert results_api.status_code == 400
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 2

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'awaitingvalidation'

        clear_purge()

@pytest.mark.functional
def test_update_from_3_to_5_should_not_update():
    """
   Author name :Daniel.A
   Description: check update order status StockConfirmed (3) to status shipped (5) should fail.
   date:
   """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == 400

        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 3

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'stockconfirmed'

        clear_purge()

@pytest.mark.functional
def test_update_from_4_to_5_update():
    """
  Author name :Daniel.A
  Description: check update order status payment (4) to status shipped (5) successfully.
  date:
  """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

        api = OrderingAPI()
        result_api = api.update_statusId_to_shipped(order_id)
        assert result_api.status_code == 200
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'shipped'

        clear_purge()

@pytest.mark.functional
def test_update_from_6_to_5_should_not_update():
    """
   Author name :Daniel.A
   Description: check the update from status 6 to 5 when out of stock .
   date:
   """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')

        api = OrderingAPI()
        api.update_statusId_to_cancelled(order_id)
        assert api.update_statusId_to_cancelled(order_id).status_code == 200
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api = OrderingAPI()
        api.update_statusId_to_shipped(order_id)
        assert api.update_statusId_to_shipped(order_id).status_code == 400
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        clear_purge()

@pytest.mark.functional
def test_cancel_from_1_to_6_should_update():
    """
   Author name :Daniel.A
   Description: check cancel order status Submitted (1) to status cancelled (6). can be cancelled only with
    statuses (submitted, awaitingValidation, stockConfirmed) successfully.
   date:
   """
    docker = DockerManager()
    message = Message()
    message.order_data()
    try:
        docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)

            # Verify that the order status is 'created'
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            # Retrieve the ID of the last created order
            order_id = get_id_of_last_order()[0]['id']

            api = OrderingAPI()
            update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
            assert update_statusId_to_cancelled_api.status_code == 200
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 6

            api_get_order_by_id = api.get_order_by_id(order_id)
            assert api_get_order_by_id.status_code == 200
            assert api_get_order_by_id.json()['status'] == 'cancelled'

    finally:
        docker.start('eshop/ordering.backgroundtasks:linux-latest')
        clear_purge()

@pytest.mark.functional
def test_cancel_from_2_to_6_should_update():
    """
   Author name :Daniel.A
   Description: check cancel order status awaitingValidation (2) to status cancelled (6). can be cancelled only with
    statuses (submitted, awaitingValidation, stockConfirmed) successfully.
   date:
   """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == 200
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'cancelled'

        clear_purge()

@pytest.mark.functional
def test_cancel_from_3_to_6_should_update():
    """
   Author name :Daniel.A
   Description: check cancel order status stockConfirmed (3) to status cancelled (6). can be cancelled only with
   statuses (submitted, awaitingValidation, stockConfirmed) successfully.
   date:
   """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == 200
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 6

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'cancelled'

        clear_purge()

@pytest.mark.functional
def test_cancel_from_4_to_6_should_not_update():
    """
      Author name :Daniel.A
      Description: check cancel order status payment (4) to status cancelled (6) should fail.
      date:
      """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

        api = OrderingAPI()
        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == 400
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 4

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'paid'

        clear_purge()

@pytest.mark.functional
def test_cancel_from_5_to_6_should_not_update():
    """
      Author name :Daniel.A
      Description: check cancel order status Shipped (5) to status cancelled (6)  should fail.
      date:
      """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

        api = OrderingAPI()
        api.update_statusId_to_shipped(order_id)
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        update_statusId_to_cancelled_api = api.update_statusId_to_cancelled(order_id)
        assert update_statusId_to_cancelled_api.status_code == 400
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 5

        api_get_order_by_id = api.get_order_by_id(order_id)
        assert api_get_order_by_id.status_code == 200
        assert api_get_order_by_id.json()['status'] == 'shipped'

        clear_purge()

@pytest.mark.Reliability
def test_create_order_when_ordering_service_down():
    """
      Author name :Daniel.A
      Description: check how ordering handles when the service is shut down while in process.
      date:
      """
    docker = DockerManager()
    try:
        docker.stop('eshop/ordering.api:linux-latest')
        message = Message()
        message.order_data()
        with RabbitMQ() as mq:
            docker.start('eshop/ordering.api:linux-latest')
            time.sleep(5)
            mq.consume('Basket', callback)

            # Verify that the order status is 'created'
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            # Retrieve the ID of the last created order
            order_id = get_id_of_last_order()[0]['id']

            # Wait for the order status to change to 'awaiting validation'
            wait_for_order_status(2)

            # Confirm the catalog input for the order
            mq.consume('Catalog', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
            message.catalog_input_confirmed(order_id)

            # Wait for the order status to change to 'stock confirmed'
            wait_for_order_status(3)

            # Confirm the payment input for the order
            mq.consume('Payment', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
            message.payment_input_succeed(order_id)

            # Wait for the order status to change to 'paid'
            wait_for_order_status(4)

            # Verify that the order status is updated to 'paid' in the catalog
            mq.consume('Catalog', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToPaid')

    finally:
        docker.start('eshop/ordering.api:linux-latest')

@pytest.mark.Reliability
def test_create_order_when_ordering_service_restarts():
    """
      Author name :Daniel.A
      Description: check how ordering handles when the service get restart while in process.
      date:
      """
    docker = DockerManager()
    message = Message()
    message.order_data()
    order_status = None
    with RabbitMQ() as mq:
        docker.restart('eshop/ordering.api:linux-latest')
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

@pytest.mark.Scalability
def test_create_100_new_orders():
    """
      Author name :Daniel.A
      Description: check how ordering handles with 100 creating request in one hour.
      date:
      """
    message = Message()
    begin_time = time.time()
    for i in range(10):
        message.order_data()
        with RabbitMQ() as mq:
            mq.consume('Basket', callback)

            # Verify that the order status is 'created'
            results = get_status_of_last_order()
            assert results[0]['orderstatusid'] == 1

            # Retrieve the ID of the last created order
            order_id = get_id_of_last_order()[0]['id']

            # Wait for the order status to change to 'awaiting validation'
            wait_for_order_status(2)

            # Confirm the catalog input for the order
            mq.consume('Catalog', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
            message.catalog_input_confirmed(order_id)

            # Wait for the order status to change to 'stock confirmed'
            wait_for_order_status(3)

            # Confirm the payment input for the order
            mq.consume('Payment', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
            message.payment_input_succeed(order_id)

            # Wait for the order status to change to 'paid'
            wait_for_order_status(4)

            # Verify that the order status is updated to 'paid' in the catalog
            mq.consume('Catalog', callback)
            assert routing_key() == os.getenv('OrderStatusChangedToPaid')

    end_time = time.time()
    sum_of_time = begin_time - end_time
    assert sum_of_time < 3600

@pytest.mark.Security
def test_create_order_when_user_not_exist_in_db():
    """
    Author name :Daniel.A
    Description: check if order created when user not exist in db should fail.
    date:
    """

    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(user_id=os.getenv('USER_ID_NOT_EXIST_IN_DB'), username='wrong',
                       buyer_id=os.getenv('BUY_ID_NOT_EXIST_IN_DB'))
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_order_when_there_is_no_zipcode():
    """
  Author name :Daniel.A
  Description: check when creating order with a zipcode not valid (chars) insert only chars
  , order should not be created.
  date:
  """
    count_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(zip_code="")
    count_of_the_orders_after = get_order_count()
    assert count_of_the_orders_before[0][''] == count_of_the_orders_after[0]['']

# its let me create the order. is it bug?
# this is a bug I can create order with chars if the len of them is between 10 and 20.
@pytest.mark.Functional
def test_create_new_order_card_number_not_valid_only_chars():
    """
     Author name :Daniel.A
     Description: check if order created when cardNumber build from only strings not valid should fail.
     date:
     """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_number="asdasdasdafdfdd")
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_order_when_cardTypeId_not_valid_number_not_defined():
    """
     Author name :Daniel.A
     Description: check create new order when CardTypeId not valid - with number that was not defined,
     should not create new order in db.
     date:
     """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_type_id=500)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_new_order_when_CardExpiration_expired():
    """
    Author name :Daniel.A
    Description: check creating order when CardExpiration expired,
    should not create new order.
    date:
    """
    message = Message()
    len_of_the_orders_before = get_order_count()
    message.order_data(card_expiration="2000-12-31T22:00:00Z")
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_new_order_when_CardTypeId_not_valid_only_chars():
    """
    Author name :Daniel.A
    Description: check create new order when CardTypeId not valid,
    should not create new order in db.
    date:
    """

    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_type_id='wrong')
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_new_order_when_CardTypeId_not_valid_only_chars_with_number_defined():
    """
    Author name :Daniel.A
    Description: check create new order when CardTypeId not valid with number that defined,
    should not create new order in db.
    date:
    """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_type_id='1')
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_new_order_when_card_security_number_not_valid_only_chars():
    """
   Author name :Daniel.A
   Description: check create new order when CardSecurityNumber not valid,
   should not create new order in db.
   date:
   """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_security_number="wrong")
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

# gives me to create order when card security number wrong (BUG?)
@pytest.mark.Functional
def test_create_new_order_when_insert_wrong_CardSecuirtyNumber():
    """
   Author name :Daniel.A
   Description: check create new order when inserting wrong CardSecurityNumber,
   should not create new order in db.
   date:
   """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(card_security_number="777")
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']


@pytest.mark.Functional
def test_create_new_order_with_negative_number_of_items():
    """
      Author name :Daniel.A
      Description: check when creating order with a negative number in the quantity of items,
      order should not be created.
      date:
      """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(quantity=-100)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

@pytest.mark.Functional
def test_create_new_order_with_zero_items():
    """
      Author name :Daniel.A
      Description: check when creating order with a zero in the quantity of items,
      order should not be created.
      date:
      """
    message = Message()
    len_of_the_orders_before = get_order_count()
    message.order_data(quantity=0)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

# created order with product id that doesn't exist in the db (bug)?
@pytest.mark.Functional
def test_create_new_order_with_productId_that_not_exist_in_db():
    """
     Author name :Daniel.A
     Description: check when creating order with a product id that doesn't  exist in the db.
     ,order should not be created.
     date:
     """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(product_id=1000000)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']


@pytest.mark.Functional
def test_create_new_order_with_productId_not_valid_string():
    """
    Author name :Daniel.A
    Description: : check when creating order with a product id not valid insert string.
    ,order should not be created.
    date:
    """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(product_id="wrong")
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

# creating new order when given product id not valid (BUG) !
@pytest.mark.Functional
def test_create_new_order_with_productId_not_valid_negative_numbers():
    """
    Author name :Daniel.A
    Description: : check when creating order with a product id not valid insert only negative numbers
    ,order should not be created.
    date:
    """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(product_id=-2000)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']


@pytest.mark.Functional
def test_create_new_order_with_price_not_valid_negative_numbers():
    """
    Author name :Daniel.A
    Description: : : check when creating order with a price of item not valid insert negative numbers.
    , order should not be created.
    date:
    """
    len_of_the_orders_before = get_order_count()
    message = Message()
    message.order_data(unit_price=-550)
    time.sleep(2)
    len_of_the_orders_after = get_order_count()
    assert len_of_the_orders_before[0][''] == len_of_the_orders_after[0]['']

# getting the order of another user BUG !!!
@pytest.mark.Security
def test_get_orderid_of_another_user_bob_to_alice():
    """
    Author name :Daniel.A
    Description: :check if user can get order of another user, should fail.
    date:
    """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')

        user = OrderingAPI("bob", "Pass123$")
        update_response = user.get_order_by_id(order_id)
        assert update_response.status_code == 400

# canceling order of another user BUG !!!
@pytest.mark.Security
def test_cancel_order_of_another_user_bob_to_alice():
    """
    Author name :Daniel.A
    Description: :check if user can get order of another user, should fail.
    date:
    """
    message = Message()
    message.order_data()
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')

    user = OrderingAPI("Bob","Pass123$")
    update_response = user.update_statusId_to_cancelled(order_id)
    assert update_response.status_code == 400

# updating order of another user BUG !!!
@pytest.mark.Security
def test_update_order_of_another_user_bob_to_alice():
    """
    Author name :Daniel.A
    Description: :check if user can get order of another user, should fail.
    date:
    """
    message = Message()
    message.order_data()
    # Create a new order and verify that it has started processing
    with RabbitMQ() as mq:
        mq.consume('Basket', callback)

        # Verify that the order status is 'created'
        results = get_status_of_last_order()
        assert results[0]['orderstatusid'] == 1

        # Retrieve the ID of the last created order
        order_id = get_id_of_last_order()[0]['id']

        # Wait for the order status to change to 'awaiting validation'
        wait_for_order_status(2)

        # Confirm the catalog input for the order
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToAwaitingValidation')
        message.catalog_input_confirmed(order_id)

        # Wait for the order status to change to 'stock confirmed'
        wait_for_order_status(3)

        # Confirm the payment input for the order
        mq.consume('Payment', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToStockConfirmed')
        message.payment_input_succeed(order_id)

        # Wait for the order status to change to 'paid'
        wait_for_order_status(4)

        # Verify that the order status is updated to 'paid' in the catalog
        mq.consume('Catalog', callback)
        assert routing_key() == os.getenv('OrderStatusChangedToPaid')

        user = OrderingAPI('Bob','Pass123$')
        update_response = user.update_statusId_to_shipped(order_id)
        assert update_response.status_code == 400





