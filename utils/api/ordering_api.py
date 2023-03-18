import uuid

import requests

from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}", "x-requestid": str(uuid.uuid4())}
        self.invalid_header = {"Authorization": "123alice", "x-requestid": str(uuid.uuid4())}

    def get_order_by_id(self, order_id):
        """
        Method to Get order by id.
        :param order_id: The order id.
        :return: Json response for the request.
        """
        return requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)

    def get_orders(self):
        """
        Method to Get orders.
        :return: Json response for the request.
        """
        return requests.get(f'{self.base_url}/api/v1/orders', headers=self.headers)

    def get_card_types(self):
        """
        Method to Get card types from the ordering API.
        :return: Json response for the API request.
        """
        return requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)

    def cancel_order(self, order_number):
        """
        Method to cancel order.
        :param order_number: The order number to cancel.
        :return: Json response for the request.
        """
        pyload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=self.headers, json=pyload)

    def ship_order(self, order_number):
        """
        Method to Get ship order.
        :param order_number: The order number to ship.
        :return: Json response for the request.
        """
        payload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/ship', json=payload,
                            headers=self.headers)

    def get_order_by_id_invalid_auth(self, order_id):
        """
        Method to send invalid an API request to get order by id.
        :param order_id: The order id we try to fetch.
        :return: Json response for the request.
        """
        return requests.get(f'{self.invalid_header}/api/v1/orders/{order_id}', headers=self.headers)

    def get_orders_invalid_auth(self):
        """
        Method to send invalid an API request to get all orders.
        :return: Json response for the request.
        """
        return requests.get(f'{self.base_url}/api/v1/orders', headers=self.invalid_header)

    def get_card_types_invalid_auth(self):
        """
        Method to send invalid an API request to get card types.
        :return: Json response for the request.
        """
        return requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.invalid_header)

    def cancel_order_invalid_auth(self, order_number):
        """
        Method to send invalid an API request to cancel order.
        :return: Json response for the request.
        """
        pyload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=self.invalid_header, json=pyload)

    def ship_order_invalid_auth(self, order_number):
        """
        Method to send invalid an API request to cancel order.
        :return: Json response for the request.
        """
        payload = {"orderNumber": order_number}
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', json=payload,
                            headers=self.invalid_header)
