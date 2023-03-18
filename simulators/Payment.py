from dotenv import load_dotenv
from simulators.Simulator import Simulator
import os


class Payment(Simulator):
    
    load_dotenv()

    def __init__(self):
        super().__init__()
    
    def order_inventory_confirmed(self):
        super(Payment, self).receive(queue='Payment' ,routing_key=os.getenv('ORDER_INVENTORY_CONFIRMED'))
    
    def payment_succeeded(self):
        self.body['message1.6']['OrderId'] = self.last_order
        super(Payment, self).send(body=self.body['message1.6'], routing_key=os.getenv('ORDER_PAYMENT_SUCCEEDED'))
    
    def payment_failed(self):
        self.body['message1.7']['OrderId'] = self.last_order
        super(Payment, self).send(body=self.body['message1.7'], routing_key=os.getenv('ORDER_PAYMENT_FAILES'))
    
