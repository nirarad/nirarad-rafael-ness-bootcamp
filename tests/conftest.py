import pytest
from dotenv import load_dotenv

from simulators.simulator import Simulator


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(autouse=True)
def purge_all_queues():
    """
    Fixture to purge all messages in each queue, to run before every test.
    """
    Simulator.purge_all_queues(
        ['Ordering', 'Basket', 'Catalog', 'Payment', 'Ordering.signalrhub', 'Webhooks', 'BackgroundTasks'])
