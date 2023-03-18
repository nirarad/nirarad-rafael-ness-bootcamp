from dotenv import load_dotenv
from simulators.Simulator import Simulator
import os


class Catalog(Simulator):
    
    load_dotenv()

    def __init__(self):
        super().__init__()
    
    def verify_item_in_stock(self):
        super(Catalog, self).receive(queue='Catalog' ,routing_key=os.getenv('VERIFY_ITEM'))
    
    def item_in_stock(self):
        self.body['message1.2']['OrderId'] = self.last_order
        super(Catalog, self).send(body=self.body['message1.2'], routing_key=os.getenv('ORDER_STOCK_CONFIRMED'))
    
    def item_out_of_stock(self):
        self.body['message1.3']['OrderId'] = self.last_order
        super(Catalog, self).send(body=self.body['message1.3'], routing_key=os.getenv('ORDER_STOCK_REJECTED'))

