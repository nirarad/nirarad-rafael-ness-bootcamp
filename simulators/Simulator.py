
from dotenv import load_dotenv
import sys
sys.path.insert(0, r'C:\Users\Hana Danis\Downloads\Bootcamp-automation\esh\eShopOnContainersPro\rafael-ness-bootcamp')
from utils.rabbitmq.rabbitmq_send import RabbitMQ
from utils.db.db_utils import MSSQLConnector
from utils.db.Useful_queries import Queries
import json
import os


class Simulator:
    
    load_dotenv()
    queries = Queries()

    def __init__(self):
        self.json_path = os.getenv('JSON_PATH')
        with open(self.json_path, 'r') as f:
            self.body = json.load(f)
        self.last_order = Simulator.queries.get_last_ordering()
    
    def send(self, body, routing_key):
        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
            routing_key=routing_key,
            body=json.dumps(body))
        
    def callback(self, ch, method, properties, body):
        if method.routing_key != None:
            ch.stop_consuming()
            
    def receive(self, queue, routing_key):
        with RabbitMQ() as mq:
            mq.consume(queue, self.callback)
        if routing_key != '':
            return True
        else:
            return False

    
    


            
