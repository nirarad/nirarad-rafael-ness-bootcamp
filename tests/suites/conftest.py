import threading
from time import sleep

import pytest
from dotenv import load_dotenv

from config.constants import *
from tests.scenarios.multi_threading_scenarios import CreateOrderThread, GetOrdersRequestsThread
from utils.docker.docker_utils import DockerManager
from utils.eshop.eshop_system_utils import EShopSystem


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Fixture to load the environment variables one time before all tests execution.
    """
    load_dotenv()


@pytest.fixture()
def setup_docker_containers():
    """
    Fixture to start all containers except the containers that have a representative simulator.
    """
    docker_manager = DockerManager()
    print("Setting up docker containers...")

    representative_simulators_containers = [CATALOG_SERVICE, PAYMENT_SERVICE,
                                            BASKET_SERVICE]

    # Start all containers, only if the current running containers amount is invalid.
    if len(docker_manager.running_containers) != len(docker_manager.containers) - len(
            representative_simulators_containers):
        docker_manager.start_all_containers()
        sleep(3)
        # Verify all containers are up and running
        docker_manager.start_all_containers()

        # Stop all containers that have a related simulator
        for container_name in representative_simulators_containers:
            docker_manager.stop(container_name)

        sleep(10)

        docker_manager.force_start(IDENTITY_SERVICE_ID)


@pytest.fixture(autouse=True)
def purge_all_queues(setup_docker_containers):
    """
    Fixture to purge all messages in each queue before every test.
    """
    print("Purge all queues...")
    EShopSystem.purge_all_queues(
        [ORDERING_QUEUE_NAME, BASKET_QUEUE_NAME, CATALOG_QUEUE_NAME, PAYMENT_QUEUE_NAME, SIGNALR_HUB_QUEUE_NAME,
         WEBHOOKS_QUEUE_NAME, BACKGROUND_TASK_QUEUE_NAME])
    sleep(2)
    EShopSystem.purge_all_queues(
        [ORDERING_QUEUE_NAME, BASKET_QUEUE_NAME, CATALOG_QUEUE_NAME, PAYMENT_QUEUE_NAME, SIGNALR_HUB_QUEUE_NAME,
         WEBHOOKS_QUEUE_NAME, BACKGROUND_TASK_QUEUE_NAME])
    sleep(1)


@pytest.fixture()
def ddos_simulation():
    """
    Fixture that construct 2 ddos_simulation threads to simulate a ddos attack.
    """
    # Create the two ddos_simulation threads
    stop_event = threading.Event()
    create_order_thread = CreateOrderThread(goal=2, flag=stop_event)
    request_orders_thread = GetOrdersRequestsThread(flag=stop_event)

    # Tear down the services
    yield create_order_thread, request_orders_thread, stop_event

    # Set the event to stop the send_message_to_create_an_order thread
    stop_event.set()

    # Join the ddos_simulation at the end of the test
    create_order_thread.join()
    request_orders_thread.join()
