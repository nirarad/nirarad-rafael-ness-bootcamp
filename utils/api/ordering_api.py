import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.get_order_by_id(1).json())
