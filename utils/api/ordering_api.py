import requests
import uuid
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def cancel_order(self, order_number):
        url = f"{self.base_url}/api/v1/orders/cancel"
        headers = {'x-requestid': str(uuid.uuid4()),
                   "Authorization": f"Bearer {self.bearer_token}"
                   }
        body = {"orderNumber": order_number}
        response = requests.put(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()

    def status_shipped(self, order_id):
        url = f"{self.base_url}/api/v1/orders/ship"
        headers = {
            'x-requestid': str(uuid.uuid4()),
            'Authorization': f'Bearer {self.bearer_token}'
        }
        data = {
            "orderNumber": order_id
        }
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_order_id(self, order_number):
        url = f"{self.base_url}/api/v1/orders/{order_number}"
        order = requests.get(url, headers=self.headers)
        order.raise_for_status()
        return order.json()

    def get_orders(self):
        url = f"{self.base_url}/ordering-api/api/v1/Orders"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_card_type(self):
        url = f"{self.base_url}/api/v1/orders/cardtypes"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()




if __name__ == '__main__':
    import pprint

    api = OrderingAPI()
    #pprint.pprint(api.get_order_by_id(25).json())
    pprint.pprint(api.get_orders())

