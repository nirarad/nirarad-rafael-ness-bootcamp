import uuid

import requests

from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "x-requestid": str(uuid.uuid4())
        }

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_orders(self):
        orders = requests.get(f'{self.base_url}/api/v1/orders', headers=self.headers)
        # pprint(orders.text)
        return orders

    def get_cardtypes(self):
        cardtypes = requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)
        return cardtypes

    def cancel_order(self, order_id):
        orders = requests.put(
            f'{self.base_url}/api/v1/orders/cancel',
            json={
                "orderNumber": order_id
            }, headers=self.headers)
        # pprint(orders.text)
        return orders

    def ship_order(self, order_id):
        orders = requests.put(
            f'{self.base_url}/api/v1/orders/ship',
            json={
                "orderNumber": order_id
            }, headers=self.headers)
        # pprint(orders.text)
        return orders


if __name__ == '__main__':
    import pprint

    api = OrderingAPI()
    pprint.pprint(api.get_orders())
