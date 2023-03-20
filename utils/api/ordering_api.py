import requests
from utils.api.bearer_tokenizer import BearerTokenizer
import uuid
import sys
sys.path.insert(0, r'C:\Users\Hana Danis\Downloads\Bootcamp-automation\esh\eShopOnContainersPro\rafael-ness-bootcamp')


class OrderingAPI:

    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
    
    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order
    
    def get_orders(self):
        order = requests.get(f'{self.base_url}/api/v1/orders', headers=self.headers)
        return order
    
    def cancel_order_by_id(self, order_id):
        body = {"orderNumber" : order_id}
        headers = self.headers
        headers['x-requestid'] = str(uuid.uuid4())
        order = requests.put(f'{self.base_url}/api/v1/Orders/cancel',json=body, headers=headers)
        return order   

    def ship_order_by_id(self, order_id):
        body = {"orderNumber" : order_id}
        headers = self.headers
        headers['x-requestid'] = str(uuid.uuid4())
        order = requests.put(f'{self.base_url}/api/v1/Orders/ship',json=body, headers=headers)
        return order 
    
    def get_ordernumber_by_username_and_password(self,username='bob', password='Pass123$'):
        bearer_token = BearerTokenizer(username, password).bearer_token
        headers = {"Authorization": f"Bearer {bearer_token}"}
        order = requests.get(f'{self.base_url}/api/v1/orders', headers=headers)
        if len(order.json()) != 0:
            return order.json()[0]['ordernumber']
        else:
            return 0