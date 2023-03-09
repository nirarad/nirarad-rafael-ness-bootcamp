import json

from utils.docker.docker_utils import DockerManager
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.ddt import json_read
import pytest

DockerManager()
RabbitMQ()
data = json_read.data_from_json('../utils/ddt/json_file.json')

# @pytest.fixture
# def dockermanager():
#     return DockerManager()


@pytest.mark.test_Create_Order_MSS
def test_create_order_mss():
    """
    This test check create order - mss
    :param
    """
    for name in data:
        try:
            with RabbitMQ() as mq:
                mq.publish(exchange='eshop_event_bus',
                           routing_key=name["RoutingKey"],
                           body=json.dumps(name["Body"]))
            # assert homepage.first_name_is_valid() == True
            # testwriteToFile(f'{test_func_name} {param}  {name[first_name]} {is_valid} {test_pass}', test_name)
        except:
            pass
            # homepage.screenshot(test_name=test_name)
            # testwriteToFile(f'{test_func_name} {param}  {name[first_name]} {is_not_valid} {test_fail}', test_name)
