from time import sleep

import pytest

from tests.scenarios.scenarios import *


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_1_and_2(docker_manager, rabbit_mq, mssql_connector):
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes in between the ‘submitted’ to the ‘awaitingvalidation’ state.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 34

    Source Test Case Traceability: 7.1
    """
    # Set pre-conditions: Stop the ordering service, and his background task.
    sleep(5)
    docker_manager.stop("eshop/ordering.signalrhub:linux-latest")
    docker_manager.stop("eshop/ordering.backgroundtasks:linux-latest")
    docker_manager.stop("eshop/ordering.backgroundtasks:linux-latest")
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

    # Step 3-4: Simulate the ordering service crash.
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
def test_valid_data_recovery_on_crash_between_status_2_and_3(docker_manager, rabbit_mq, mssql_connector):
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes between the ‘awaitingvalidation’ and ‘stockconfirmed’ states.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 35

    Source Test Case Traceability: 7.2
    """
    # Set pre-conditions: Stop the ordering.singlerhub service.
    sleep(5)
    docker_manager.stop("eshop/ordering.signalrhub:linux-latest")
    sleep(5)

    # Verify that both of the queues are empty.
    if not rabbit_mq.validate_queue_is_empty('Ordering'):
        rabbit_mq.purge_queue('Ordering')
    if not rabbit_mq.validate_queue_is_empty('Basket'):
        rabbit_mq.purge_queue('Basket')
    if not rabbit_mq.validate_queue_is_empty('Catalog'):
        rabbit_mq.purge_queue('Catalog')

    messages_amount_to_send = 3
    for _ in range(3):
        order_submission_without_response_waiting_scenario()

    #  When the order status changes to 2, simulate the ordering service crash.
    if Simulator.explicit_status_id_validation(2, 50, Simulator.get_max_order_id()):
        crash_ordering_service_scenario(docker_manager, service_name_list=["eshop/ordering.api:linux-latest",
                                                                           "eshop/ordering.backgroundtasks:linux-latest",
                                                                           "eshop/ordering.signalrhub:linux-latest"])
    sleep(5)

    # Verify that there are still n messages in the order queue, or in the catalog queue, or distributed in both queues.
    message_counter = 0
    for queue in ["Ordering", "Catalog"]:
        message_counter += rabbit_mq.get_number_of_messages_in_queue(queue)

    assert message_counter == messages_amount_to_send

    # Step 6: Start the ordering service (both api and background task services).
    docker_manager.start("eshop/ordering.api:linux-latest")
    docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")

    # Step 7: Verify that n order entities have been created within the ordering table, with OrderStatusID of 2 or 3.
    assert Simulator.select_top_n_orders_same_status(
        mssql_connector=mssql_connector, status_number_1=3,
        status_number_2=2, amount_of_orders=3, timeout=10)


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_between_status_3_and_4(docker_manager, rabbit_mq, mssql_connector):
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes between the ‘stockconfirmed’ and ‘paid’ states.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 36

    Source Test Case Traceability: 7.3
    """
    # Set pre-conditions: Stop the ordering.singlerhub service.
    crash_ordering_service_scenario(docker_manager, service_name_list=["eshop/ordering.api:linux-latest",
                                                                       "eshop/ordering.backgroundtasks:linux-latest",
                                                                       "eshop/ordering.signalrhub:linux-latest"])
    sleep(5)

    # Verify that both of the queues are empty.
    if not rabbit_mq.validate_queue_is_empty('Ordering'):
        rabbit_mq.purge_queue('Ordering')
    if not rabbit_mq.validate_queue_is_empty('Basket'):
        rabbit_mq.purge_queue('Basket')
    if not rabbit_mq.validate_queue_is_empty('Catalog'):
        rabbit_mq.purge_queue('Catalog')

    # Send the messages for waiting in the ordering queue.
    messages_amount_to_send = 3
    for _ in range(messages_amount_to_send):
        order_submission_without_response_waiting_scenario()
        docker_manager.start("eshop/ordering.api:linux-latest")
        docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")
        crash_ordering_service_scenario(docker_manager)
        catalog_stock_confirmation_without_waiting_for_response_scenario()

    # Start the ordering service (both api and background task services).
    docker_manager.start("eshop/ordering.api:linux-latest")
    docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")

    # Wait for the id to be 2.
    if Simulator.explicit_status_id_validation(3, 60, Simulator.get_max_order_id()):
        #  When the order status changes to 3, simulate the ordering service crash.
        crash_ordering_service_scenario(docker_manager, service_name_list=["eshop/ordering.api:linux-latest",
                                                                           "eshop/ordering.backgroundtasks:linux-latest",
                                                                           "eshop/ordering.signalrhub:linux-latest"])
    sleep(5)

    # Verify that there are still n messages in the order queue, or in the catalog queue, or distributed in both queues.
    message_counter = 0
    for queue in ["Ordering", "Payment"]:
        message_counter += rabbit_mq.get_number_of_messages_in_queue(queue)

    assert message_counter == messages_amount_to_send

    # Step 6: Start the ordering service (both api and background task services).
    docker_manager.start("eshop/ordering.api:linux-latest")
    docker_manager.start("eshop/ordering.backgroundtasks:linux-latest")

    # Step 7: Verify that n order entities have been created within the ordering table, with OrderStatusID of 2 or 3.
    assert Simulator.select_top_n_orders_same_status(
        mssql_connector=mssql_connector, status_number_1=4,
        status_number_2=3, amount_of_orders=3, timeout=10)
