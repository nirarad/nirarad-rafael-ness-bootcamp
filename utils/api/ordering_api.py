import uuid
import requests
from utils.api.bearer_tokenizer import BearerTokenizer

class OrderingAPI:
    def __init__(self,username,password):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username,password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_orders(self):
        order = requests.get(f'{self.base_url}/api/v1/orders/', headers=self.headers)
        return order

    def get_card_types(self):
        order = requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)
        return order

    def post_draft(self):
        order = requests.post(f'{self.base_url}/api/v1/orders/draft', headers=self.headers)
        return order
    def cancel_order(self, order_id):
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body = {"orderNumber": order_id}
        order = requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=headers, json=body)
        return order

    def put_change_status_to_shipped(self, order_id):
        headers = {'x-requestid': str(uuid.uuid4()),'Authorization': f'Bearer {self.bearer_token}'}
        body = {"orderNumber": order_id}
        order = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=body)
        return order


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    # pprint.pprint(api.get_order_by_id(1).json())
    # pprint.pprint(api.get_orders().json())
    # pprint.pprint(api.get_card_types().json())
    # pprint.pprint(api.post_draft().json())
    # pprint.pprint(api.cancel_order(1022).json())
    pprint.pprint(api.get_orders().json())
    if api.status_code() == 200:
        print("yess")


