import requests
import uuid
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_orders(self):
        all_orders = requests.get(f'{self.base_url}/api/v1/Orders', headers=self.headers)
        return all_orders

    def get_cardTypes(self):
        card_types = requests.get(f'{self.base_url}/ordering-api/api/v1/Orders/cardtypes', headers=self.headers)
        return card_types

    def update_statusId_to_shipped(self,order_id):
        data = {
                "orderNumber": order_id
            }
        headers = {'x-requestid': str(uuid.uuid4()), 'Authorization': f'Bearer {self.bearer_token}'}
        status = requests.put(f'{self.base_url}/api/v1/orders/ship',headers=headers,json=data)
        return status


    def update_statusId_to_cancelled(self,order_id):
        data = {
            "orderNumber": order_id
        }
        headers = {'x-requestid': str(uuid.uuid4()), 'Authorization': f'Bearer {self.bearer_token}'}
        status = requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=headers, json=data)
        return status




if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    # pprint.pprint(api.get_order_by_id(1).json())
    # #pprint.pprint(api.get_orders())
    # #pprint.pprint(api.get_cardTypes().json())
    # pprint.pprint(api.update_statusId_to_shipped(1468))
    pprint.pprint(api.update_statusId_to_cancelled(630))



