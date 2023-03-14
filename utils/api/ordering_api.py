import json
import uuid

import requests
import pprint

from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.body = None

    def call_server(self):
        """
        function which call the ordering-API server by basic get
        request and return status of the connection
        :return int:
        """
        endpoint = f'{self.base_url}'
        try:
            response = requests.get(endpoint, headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return response.status_code

    def get_orders(self):
        """
        function which call the ordering-API server by get
        request and return user's orders list
        :return list:
        """
        try:
            endpoint = f'{self.base_url}/ordering-api/api/v1/Orders'
            response = requests.get(endpoint, headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return response

    def get_order_by_id(self, order_id, auth=True):
        """
        function which call the ordering-API server by get
        request and return user's list by id
        :param order_id:
        :param auth:
        :return:
        """
        if not str(order_id).isnumeric():
            raise ValueError("order id have to be a number")
        try:
            endpoint = f'{self.base_url}/api/v1/orders/{order_id}'
            if auth:
                response = requests.get(endpoint, headers=self.headers)
            else:
                wrong_header = {'Authorization': self.headers["Authorization"] + "a"}
                response = requests.get(endpoint, headers=wrong_header)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return response

    def cancel_order(self, order_id):
        """
        function which call the ordering-API server by put
        request and cancel order by id
        :param order_id:
        :return:
        """
        self.headers['Content-Type'] = 'application/json'
        self.headers['x-requestid'] = str(uuid.uuid4())
        if not str(order_id).isnumeric():
            raise ValueError("order id have to be a number")
        try:
            endpoint = f'{self.base_url}/ordering-api/api/v1/Orders/cancel'
            self.body = {"orderNumber": order_id}
            response = requests.put(url=endpoint, data=json.dumps(self.body), headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return response

    def ship_order(self, order_id):
        """
        function which call the ordering-API server by put
        request and ship order by id
        :return:
        """
        self.headers['Content-Type'] = 'application/json'
        self.headers['x-requestid'] = str(uuid.uuid4())
        if not str(order_id).isnumeric():
            raise ValueError("order id have to be a number")
        try:
            endpoint = f'{self.base_url}/ordering-api/api/v1/Orders/ship'
            self.body = {"orderNumber": order_id}
            response = requests.put(url=endpoint, data=json.dumps(self.body), headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return response


if __name__ == '__main__':
    api = OrderingAPI()
    pprint.pprint(api.get_order_by_id(1).json())

