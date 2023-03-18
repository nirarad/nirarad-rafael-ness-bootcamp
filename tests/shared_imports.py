import sys
sys.path.insert(1, r'C:\Users\Hana Danis\Downloads\Bootcamp-automation\esh\eShopOnContainersPro\rafael-ness-bootcamp')
from simulators.Catalog import Catalog
from simulators.Payment import Payment
from simulators.Simulator import Simulator
from simulators.Basket import Basket
from utils.docker.docker_utils import DockerManager
import os
from dotenv import load_dotenv
from utils.db.Useful_queries import Queries
from utils.api.ordering_api import OrderingAPI
import pytest

queries = Queries()
load_dotenv()
dm = DockerManager()
basket = Basket()
payment = Payment()
catalog = Catalog()
simulator = Simulator()
orderingAPI = OrderingAPI()