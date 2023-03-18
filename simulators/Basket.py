from dotenv import load_dotenv
from simulators.Simulator import Simulator
import uuid
import os

class Basket(Simulator):
    
    load_dotenv()

    def __init__(self):
        super().__init__()
 
    def create_order(self):
        self.body['message1.01']['RequestId'] = str(uuid.uuid4())
        super(Basket, self).send(body=self.body['message1.01'], routing_key=os.getenv('USER_CHECKOUT'))
        
    def remove_items_form_basket(self):
        return super(Basket, self).receive('Basket' ,os.getenv('EMPTY_BASKET'))        
        
            
