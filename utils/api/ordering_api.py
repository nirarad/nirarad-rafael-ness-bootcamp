import requests
import uuid
from utils.api.bearer_tokenizer import BearerTokenizer


class CancellationFailedException(Exception):
    pass


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def cancel_order(self, order_number):
        url = f"{self.base_url}/api/v1/orders/cancel"
        headers = {'x-requestid': str(uuid.uuid4()),
                   "Authorization": f"Bearer {self.bearer_token}"
                   }
        body = {"orderNumber": order_number}
        response = requests.put(url, headers=headers, json=body)
        return response

    def status_shipped(self, order_number):
        url = f"{self.base_url}/api/v1/orders/ship"
        headers = {
            'x-requestid': str(uuid.uuid4()),
            'Authorization': f'Bearer {self.bearer_token}'
        }
        body = {
            "orderNumber": order_number
        }
        response = requests.put(url, headers=headers, json=body)
        return response

    def get_order_id(self, order_number):
        url = f"{self.base_url}/api/v1/orders/{order_number}"
        order = requests.get(url, headers=self.headers)
        return order

    def get_orders(self):
        url = f"{self.base_url}/ordering-api/api/v1/Orders"
        response = requests.get(url, headers=self.headers)
        return response

    def get_card_type(self):
        url = f"{self.base_url}/api/v1/orders/cardtypes"
        response = requests.get(url, headers=self.headers)
        return response


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.get_orders().status_code)
    # pprint.pprint(api.get_order_by_id(25).json())
    # pprint.pprint(api.get_orders())
