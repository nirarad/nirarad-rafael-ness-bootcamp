import json
import time

from tests.server_response import *
ordering_api_container = 'eshop/ordering.api:linux-latest'
ordering_background_container = "eshop/ordering.backgroundtasks:linux-latest"

from utils.api.ordering_api import OrderingAPI
from utils.docker.docker_utils import DockerManager
from utils.db.db_utils import MSSQLConnector
import pprint
from utils.rabbitmq.rabbitmq_receive import callback
from utils.rabbitmq.rabbitmq_send import RabbitMQ

if __name__ == '__main__':
    # dm = DockerManager()
    # api = OrderingAPI()
    #
    # print(api.get_orders().json())

    for i in range(3):
        print(i)





