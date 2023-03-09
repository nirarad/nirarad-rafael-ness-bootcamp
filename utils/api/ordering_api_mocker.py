import json

import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI_Mocker:
    def __init__(self):
        self.base_url = 'http://host.docker.internal:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.base_header = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.base_header)
        return order

    def cancel_order(self, order_number=0, x_requestid=None):
        headers = {**self.base_header, **{"x-requestid": str(x_requestid)}}
        json_body = {"orderNumber": order_number}
        res = requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=headers, json=json_body)
        return res

    def ship_order(self, order_number=0, x_requestid=None):
        headers = {**self.base_header, **{"x-requestid": str(x_requestid)}}
        json_body = {"orderNumber": order_number}
        res = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=json_body)
        return res


if __name__ == '__main__':
    import pprint

    api = OrderingAPI_Mocker()
    # pprint.pprint(api.get_order_by_id(93).json())
    # pprint.pprint(api.cancel_order())
    pprint.pprint(api.ship_order(20, "43c7219a-a055-410f-847a-d7902c60d685"))
