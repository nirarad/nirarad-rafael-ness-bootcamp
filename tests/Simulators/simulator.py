import json
import uuid
import os

from Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from Utils.useful_functions import get_current_time

class Simulator:
    
    def __init__(self) -> None:
        with open(os.getenv('MESSAGES_JSON_PATH')) as j:
            self.data = json.load(j)
            self.routing_key = ''
        
    def send_message(self, routing_key, order_id=None) -> None:
        '''
        Base sending message function, receives routing key and order id as args (if necessary)
        Sends the relevant message according to the routing key from JSON file tp the eShp Event exchange.
        '''
        payload = self.data[routing_key]
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        if 'RequestId' in payload:
            payload['RequestId'] = str(uuid.uuid4())

        elif order_id is not None:
            payload['OrderId'] = order_id

        with RabbitMQ() as mq:
            mq.publish(exchange=os.getenv('ESHOP_EVENT_BUS_EXCHANGE'),
                       routing_key=routing_key,
                       body=json.dumps(payload))

    def callback(self, ch, method, properties, body):
        self.routing_key = method.routing_key
        if (self.routing_key != ''):
            ch.stop_consuming()            

    def receive_message(self, queue_name):
        '''
        Base receive message, receives queue name as arg
        Listens to the selected queue for a message, and returns the routing key of the message received.
        '''
        with RabbitMQ() as mq:
            mq.consume(queue_name, self.callback)
        routing = self.routing_key
        self.routing_key = ''
        
        return routing