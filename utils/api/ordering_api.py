import time
import uuid
import requests
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order


    def ship_order_by_id(self, order_id, unauthorised=False):
        body = {"orderNumber": order_id}
        if not unauthorised:
            headers = self.headers
        else:
            headers = {}
        headers['x-requestid']=str(uuid.uuid4())
        return requests.put(f'{self.base_url}/api/v1/orders/ship', json=body, headers=headers)


    def cancel_order_by_id(self, order_id, unauthorised=False):
        body = {"orderNumber": order_id}
        if not unauthorised:
            headers = self.headers
        else:
            headers={}
        headers['x-requestid']=str(uuid.uuid4())
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', json=body, headers=headers)



if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    res = api.get_order_by_id(1).json()
    pprint.pprint(res)


