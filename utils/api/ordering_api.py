import json
import uuid

import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_orders(self):
        order = requests.get(f'{self.base_url}/api/v1/orders', headers=self.headers)
        return order

    def get_card_type(self):
        order = requests.get(f'{self.base_url}/api/v1/orders/cardtypes', headers=self.headers)
        return order

    def cancel_order(self,order_id):
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body ={
              "orderNumber": order_id
            }
        order = requests.put(f'{self.base_url}/api/v1/orders/cancel',headers=headers, json=body)
        return order
    def change_status_to_shipped(self, order_id):
        headers = {'x-requestid': str(uuid.uuid4()),
                   'Authorization': f'Bearer {self.bearer_token}'}
        body = {

              "orderNumber": order_id
            }
        order = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=body)
        return order

    def create_order(self):
        body =  {
                "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
                "Items": [
                    {
                        "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                        "ProductId": 1,
                        "ProductName": ".NET Bot Black Hoodie",
                        "UnitPrice": 19.5,
                        "OldUnitPrice": 0,
                        "Quantity": 1,
                        "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                    }
                ]
            }

        order = requests.post(f'{self.base_url}/api/v1/orders/draft', json=body, headers=self.headers)
        print(order.text)
        return order


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.create_order())
    #pprint.pprint(api.change_status_to_shipped(2))
    #pprint.pprint(api.get_order_by_id(1).json())

