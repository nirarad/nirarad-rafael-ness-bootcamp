import uuid

import requests

from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}", "x-requestid": str(uuid.uuid4())}

    def get_order_by_id(self, order_id):
        return requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)

    def get_orders(self):
        return requests.get(f'{self.base_url}/api/v1/orders', headers=self.headers)

    def get_card_types(self):
        return requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)

    def cancel_order(self, order_number):
        pyload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=self.headers, json=pyload)

    def ship_order(self, order_number):
        payload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', json=payload,
                            headers=self.headers)


if __name__ == '__main__':
    od = OrderingAPI()
    print(od.get_card_types().json())
