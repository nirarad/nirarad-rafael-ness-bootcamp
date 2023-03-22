import uuid

import requests
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username, password):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        """
        method gets order id and returns the order
        """
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_orders(self):
        """
        method returns all user orders
        """
        orders = requests.get(f'{self.base_url}/api/v1/orders/', headers=self.headers)
        return orders.json()

    def get_orders_cardtypes(self):
        """
        method returns the cars types
        """
        order = requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)
        return order

    # def post_draft(self):
    #     order = requests.post(f'{self.base_url}/api/v1/orders/draft', headers=self.headers)
    #     return order

    def cancel_order(self, order_id):
        """
        method gets an order id and cancels the order
        """
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body = {
            "orderNumber": order_id
        }
        order = requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=headers, json=body)
        return order

    def change_status_to_shipped(self, order_id):
        """
        method gets an order id and ships ir
        """
        headers = {'x-requestid': str(uuid.uuid4()), 'Authorization': f'Bearer {self.bearer_token}'}
        body = {
            "orderNumber": order_id
        }
        order = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=body)
        return order


if __name__ == '__main__':
    import pprint

    api = OrderingAPI('alice', 'Pass123$')
    # pprint.pprint(api.get_order_by_id(1).json())
    # pprint.pprint(api.get_orders())
    # pprint.pprint(api.get_orders_cardtypes().json())
    # pprint.pprint(api.cancel_order(646))
    # pprint.pprint(api.change_status_to_shipped(1195))
