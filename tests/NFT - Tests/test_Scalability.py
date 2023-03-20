import os
import sys
from datetime import datetime, timedelta
from time import sleep

import pytest
from dotenv import load_dotenv
from tests.env import env_path


from utils.db.db_utils import MSSQLConnector
from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.eshop_rabbitmq_events import create_order



@pytest.fixture()
def Scalability_scenario():
        load_dotenv(env_path)


def test_loads_message(Scalability_scenario):
    """
    # Test Case 6.1
    function that check the ability of system to contest with load of message
    :return: None
    """
    dockerManager = DockerManager()
    dockerManager.start("eshop/basket.api:linux-latest")
    dockerManager.start("eshop/catalog.api:linux-latest")
    dockerManager.start("eshop/payment.api:linux-latest")
    dockerManager.start("eshop/ordering.signalrhub:linux-latest")
    dockerManager.stop("eshop/ordering.api:linux-latest")

    for i in range(2):
        create_order(os.getenv('ALICE'))

    dockerManager.start("eshop/ordering.api:linux-latest")
    start = datetime.now()
    flag = False
    while datetime.now() < start + timedelta(minutes=3):
        with MSSQLConnector() as conn:
            t = str (start - timedelta(hours=2))
            completedOrdersNumber = conn.select_query(os.getenv('COMPLETE_ORDERS').format(t))
            completedOrdersNumber = completedOrdersNumber[0]["completedOrdersNumber"]
        if completedOrdersNumber == 2:
            flag = True
            break
        sleep(30)

    dockerManager.stop("eshop/basket.api:linux-latest")
    dockerManager.stop("eshop/catalog.api:linux-latest")
    dockerManager.stop("eshop/payment.api:linux-latest")
    dockerManager.stop("eshop/ordering.signalrhub:linux-latest")

    assert flag

















