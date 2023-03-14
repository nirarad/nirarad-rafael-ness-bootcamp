from time import sleep

import pytest

from tests.scenarios.scenarios import *


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_before_submitted(docker_manager, rabbit_mq, mssql_connector):
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes before the ‘submitted’ state.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 34

    Source Test Case Traceability: 7.1
    """
    # Pre-conditions: Stop the ordering service, and his background task.
    sleep(5)
    docker_manager.stop("eshop/ordering.api:linux-latest")
    docker_manager.stop("eshop/ordering.backgroundtasks:linux-latest")
    docker_manager.stop("eshop/ordering.signalrhub:linux-latest")
    sleep(5)

    # Verify that both of the queues are empty
    if not rabbit_mq.validate_queue_is_empty('Ordering'):
        rabbit_mq.purge_queue('Ordering')
        if not rabbit_mq.validate_queue_is_empty('Basket'):
            rabbit_mq.purge_queue('Basket')

    messages_amount_to_send = 3

    # Step 1-2: Send 5 messages to the ordering queue.
    for _ in range(messages_amount_to_send):
        order_submission_without_response_waiting_scenario()

    # Step 3: Start the ordering (both api and background task services) service.
    # Step 4: Immediately (in a maximum time of 2 second) stop the ordering service (both api and background task services).
    docker_manager.start("eshop/ordering.api:linux-latest")
    docker_manager.stop("eshop/ordering.api:linux-latest")
    docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")
    docker_manager.stop("eshop/ordering.backgroundtasks:linux-latest")
    docker_manager.stop("eshop/ordering.api:linux-latest")
    docker_manager.stop("eshop/ordering.api:linux-latest")
    sleep(10)

    # Step 5: Verify that there are still 5 messages in the order queue, or in the basket queue, or distributed in both queues.
    message_counter = 0
    for queue in ["Ordering", "Basket"]:
        message_counter += rabbit_mq.get_number_of_messages_in_queue(queue)

    assert message_counter == messages_amount_to_send

    # Step 6: Start the ordering service (both api and background task services).
    docker_manager.start("eshop/ordering.api:linux-latest")
    docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")

    # Step 7: Verify that 5 order entities have been created within the ordering table, with OrderStatusID of 1 or 2.
    assert Simulator.select_top_n_orders_same_status(
        mssql_connector=mssql_connector, status_number_1=1,
        status_number_2=2, amount_of_orders=3, timeout=10)


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_1_and_2():
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes in between the ‘submitted’ to the ‘awaitingvalidation’ state.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 35

    Source Test Case Traceability: 7.3
    """
    pass


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_1_and_2(docker_manager):
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes between the ‘awaitingvalidation’ and ‘stockconfirmed’ states.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 36

    Source Test Case Traceability: 7.4
    """
    pass


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_1_and_2():
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes between the ‘stockconfirmed’ and ‘paid’ states.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 37

    Source Test Case Traceability: 7.5
    """
    pass
