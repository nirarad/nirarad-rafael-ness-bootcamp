import json
import uuid

import requests

from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, withAuthorization):
        self.base_url = 'http://localhost:5102'
        self.headers = {}
        if withAuthorization == True:
            self.bearer_token = BearerTokenizer('alice','Pass123$').bearer_token
            self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def cancel_order(self,order_id):
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body = {
              "orderNumber": order_id
            }
        order = requests.put(f'{self.base_url}/api/v1/orders/cancel',headers=headers, json=body)
        return order
    def change_status_to_shipped(self, order_id):
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body = {

              "orderNumber": order_id
            }
        order = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=body)
        return order




if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    res=api.cancel_order(245)
    print(res.status_code)
    #pprint.pprint(api.change_status_to_shipped(2))
    #pprint.pprint(api.get_order_by_id(1).json())

