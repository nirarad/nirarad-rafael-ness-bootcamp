import pytest

from constants import *
from tests.scenarios.scenarios import *
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.ordering.ordering_service_utils import OrderingServiceUtils


@pytest.mark.scalability
@pytest.mark.loads
@pytest.mark.reliability
def test_valid_message_consumption_rate():
    """
    Source Test Case Title: Verify that the service can consume 150 messages that are waiting in the queue in a maximum time of one hour.

    Source Test Case Purpose: Verify the service can handle a large amount of messages in a given predefined time.

    Source Test Case ID: 32

    Source Test Case Traceability: 6.1
    """
    # Pre-conditions: Stop the ordering service, and his background task.
    docker_manager = DockerManager()

    with RabbitMQ() as rabbit_mq:
        sleep(5)
        docker_manager.stop(ORDERING_SERVICE)
        docker_manager.stop(ORDERING_BACKGROUND_TASK_SERVICE)
        sleep(5)

        # Step 1: Send to the ordering queue x number of messages, there suppose to waiting there, until the service is goes up again.
        for _ in range(2):
            order_submission_without_response_waiting_scenario()

        # Steps 2-3: Start the ordering service.
        docker_manager.start(ORDERING_SERVICE)
        docker_manager.start(ORDERING_BACKGROUND_TASK_SERVICE)

        # Wait for the messages to be consumed.
        sleep(5)

        # Check if the ordering queue is clear from messages.
        assert rabbit_mq.validate_queue_is_empty_while_clearing(ORDERING_QUEUE_NAME)


@pytest.mark.scalability
@pytest.mark.loads
@pytest.mark.reliability
def test_valid_pace_of_first_message_consumption():
    """
    Source Test Case Title: Verify that the service is reading the first message in the queue in a maximum time of 3 seconds.

    Source Test Case Purpose:  Verify the service does not consume the first message from its queue after more than 3 seconds.

    Source Test Case ID: 33

    Source Test Case Traceability: 6.2
    """

    # Send to the order queue a single message.
    order_submission_without_response_waiting_scenario()

    # Validate that the time to consume that message us no longer than 3 seconds.
    assert OrderingServiceUtils.get_number_of_seconds_to_consume_single_waiting_message(ORDERING_QUEUE_NAME) <= 3
