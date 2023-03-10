import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def cancel_order(self, order_id):





    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.get_order_by_id(1).json())
