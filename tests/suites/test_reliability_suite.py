import pytest

from constants import *
from tests.scenarios.scenarios import *
from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_1_and_2():
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes in between the ‘submitted’ to the ‘awaitingvalidation’ state.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 34

    Source Test Case Traceability: 7.1
    """
    docker_manager = DockerManager()
    rabbit_mq = RabbitMQ()
    mssql_connector = MSSQLConnector()
    rabbit_mq.connect()
    mssql_connector.connect()
    sleep(5)

    try:
        # Set pre-conditions: Stop the ordering service, and his background task.
        docker_manager.stop(SIGNALR_HUB_SERVICE)
        docker_manager.stop(ORDERING_BACKGROUND_TASK_SERVICE)
        docker_manager.stop(ORDERING_BACKGROUND_TASK_SERVICE)
        sleep(5)

        # Verify that both of the queues are empty.
        if not rabbit_mq.validate_queue_is_empty_once(ORDERING_QUEUE_NAME):
            rabbit_mq.purge_queue(ORDERING_QUEUE_NAME)
        if not rabbit_mq.validate_queue_is_empty_once(BASKET_QUEUE_NAME):
            rabbit_mq.purge_queue(BASKET_QUEUE_NAME)

        # to parameterize
        messages_amount_to_send = 3

        # Step 1-2: Send 5 messages to the ordering queue.
        for _ in range(messages_amount_to_send):
            order_submission_without_response_waiting_scenario()

        # Step 3-4: Simulate the ordering service crash.
        docker_manager.start(ORDERING_SERVICE)
        docker_manager.stop(ORDERING_SERVICE)
        docker_manager.start(ORDERING_BACKGROUND_TASK_SERVICE)
        docker_manager.stop(ORDERING_BACKGROUND_TASK_SERVICE)
        docker_manager.stop(ORDERING_SERVICE)
        docker_manager.stop(ORDERING_SERVICE)
        sleep(10)

        # Step 5: Verify that there are still 5 messages in the order queue, or in the basket queue, or distributed in both queues.
        message_counter = 0
        for queue in [ORDERING_QUEUE_NAME, BASKET_QUEUE_NAME]:
            message_counter += rabbit_mq.get_number_of_messages_in_queue(queue)

        assert message_counter == messages_amount_to_send

        # Step 6: Start the ordering service (both api and background task services).
        docker_manager.start(ORDERING_SERVICE)
        docker_manager.start(ORDERING_BACKGROUND_TASK_SERVICE)

        # Step 7: Verify that the given amount of order entities have been created within the ordering table, with OrderStatusID of 1 or 2.
        assert Simulator.select_top_n_orders_with_same_status(
            mssql_connector=mssql_connector, status_number_1=1,
            status_number_2=2, amount_of_orders=3, timeout=10)

    except AssertionError as a:
        raise a
    except BaseException as b:
        raise b
    finally:
        mssql_connector.close()
        rabbit_mq.close()


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_2_and_3():
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes between the ‘awaitingvalidation’ and ‘stockconfirmed’ states.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 35

    Source Test Case Traceability: 7.2
    """

    docker_manager = DockerManager()
    rabbit_mq = RabbitMQ().connect()
    mssql_connector = MSSQLConnector().connect()
    sleep(5)

    try:
        # Set pre-conditions: Stop the ordering.singlerhub service.
        docker_manager.stop(SIGNALR_HUB_SERVICE)
        sleep(5)

        # Verify that both of the queues are empty.
        if not rabbit_mq.validate_queue_is_empty_once(ORDERING_QUEUE_NAME):
            rabbit_mq.purge_queue(ORDERING_QUEUE_NAME)
        if not rabbit_mq.validate_queue_is_empty_once(BASKET_QUEUE_NAME):
            rabbit_mq.purge_queue(BASKET_QUEUE_NAME)
        if not rabbit_mq.validate_queue_is_empty_once(CATALOG_QUEUE_NAME):
            rabbit_mq.purge_queue(CATALOG_QUEUE_NAME)

        # to parameterize
        messages_amount_to_send = 3
        for _ in range(messages_amount_to_send):
            order_submission_without_response_waiting_scenario()

        #  When the order status changes to 2, simulate the ordering service crash.
        if Simulator.explicit_status_id_validation(status_id=AWAITING_VALIDATION_STATUS, timeout=50,
                                                   order_id=Simulator.get_max_order_id()):
            crash_ordering_service_scenario(docker_manager, service_name_list=[ORDERING_SERVICE,
                                                                               ORDERING_BACKGROUND_TASK_SERVICE,
                                                                               SIGNALR_HUB_SERVICE])
        sleep(5)

        # Verify that there are still n messages in the order queue, or in the catalog queue, or distributed in both queues.
        message_counter = 0
        for queue in [ORDERING_QUEUE_NAME, CATALOG_QUEUE_NAME]:
            message_counter += rabbit_mq.get_number_of_messages_in_queue(queue)

        assert message_counter == messages_amount_to_send

        # Step 6: Start the ordering service (both api and background task services).
        docker_manager.start(ORDERING_SERVICE)
        docker_manager.start(ORDERING_BACKGROUND_TASK_SERVICE)

        # Step 7: Verify that n order entities have been created within the ordering table, with OrderStatusID of 2 or 3.
        assert Simulator.select_top_n_orders_with_same_status(
            mssql_connector=mssql_connector, status_number_1=3,
            status_number_2=2, amount_of_orders=3, timeout=10)
    except AssertionError as a:
        raise a
    except BaseException as b:
        raise b
    finally:
        rabbit_mq.close()
        mssql_connector.close()
