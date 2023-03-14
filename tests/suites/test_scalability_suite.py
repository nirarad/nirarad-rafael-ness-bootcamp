import pytest


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
    pass


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
    pass
