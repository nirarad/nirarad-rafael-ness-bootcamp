from time import sleep

import pytest
from dotenv import load_dotenv

from simulators.simulator import Simulator
from utils.docker.docker_utils import DockerManager


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Fixture to load the environment variables one time before all tests execution.
    """
    load_dotenv()


@pytest.fixture(scope='session', autouse=True)
def setup_docker_containers():
    """
    Fixture to start all containers except the containers that have a related simulator.
    """
    print("Setting up docker session...")
    # Stop the mocks containers
    mocks_containers = ["eshop/catalog.api:linux-latest", "eshop/payment.api:linux-latest",
                        "eshop/basket.api:linux-latest"]
    dm = DockerManager()
    # Start all containers
    if len(dm.running_containers) != len(dm.containers) - len(mocks_containers):
        dm.start_all_containers()
        sleep(3)
        # Verify all containers are up and running
        dm.start_all_containers()

        # Stop all containers that have a related simulator
        for container_name in mocks_containers:
            dm.stop(container_name)


@pytest.fixture(autouse=True)
def purge_all_queues():
    """
    Fixture to purge all messages in each queue before every test.
    """
    Simulator.purge_all_queues(
        ['Ordering', 'Basket', 'Catalog', 'Payment', 'Ordering.signalrhub', 'Webhooks', 'BackgroundTasks'])
