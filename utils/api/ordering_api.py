import requests
import uuid


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}')
        return order


if __name__ == '__main__':
    api = OrderingAPI()
    print(api.get_order_by_id(1))
