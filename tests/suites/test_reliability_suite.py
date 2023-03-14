import pytest


@pytest.mark.reliability
def test_valid_data_recovery_on_crash_before_submitted():
    """
    Source Test Case Title: Verify that the service is able to recover the data whenever the service crashes before the ‘submitted’ state.

    Source Test Case Purpose: Verify that the service crashes, it has the ability to recover the ordering process data, from the exact point when the crash occurred.

    Source Test Case ID: 34

    Source Test Case Traceability: 7.1
    """
    pass


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
def test_valid_data_recovery_on_crash_between_status_1_and_2():
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
