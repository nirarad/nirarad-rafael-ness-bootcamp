import json
import os
import uuid
from datetime import time, datetime
import time
import requests

from log.logger import Log
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI:

    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.l = Log()

    def contact_with_the_serve(self):
        """
        Chana Kadosh
        The function connects to the API
        :return:status code
        """
        response = requests.get(f'{self.base_url}', headers=self.headers)
        return response.status_code

    def get_order_by_id(self, order_id, authorization=True):
        """
        Chana Kadosh
        The function connects to the API and returns an order by ID
        :param authorization:
        :param order_id:
        :return:order
        """
        try:
            if authorization:
                order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
                return order.json()
            else:
                order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}')
                return order
        except:
            self.l.writeLog("The function fails to connect to the API")
            raise  Exception('The function fails to connect to the API')

    def put_cancel_order(self, order_id):
        """
        Chana Kadosh
        The function connects to the API and cancels an order by ID
        :param order_id:
        :return:
        """
        try:
            url = f"{self.base_url}/api/v1/Orders/cancel"
            headers = {'x-requestid': str(uuid.uuid4()),
                       "Authorization": f"Bearer {self.bearer_token}"
                       }
            body = {"orderNumber": order_id}
            response = requests.put(url, headers=headers, json=json.dumps(body))
            return response.status_code
        except:
            self.l.writeLog("The function fails to connect to the API")
            raise Exception("The function fails to connect to the API")

    def put_change_status(self, order_id):
        try:
            url = f'{self.base_url}/ordering-api/api/v1/Orders/ship'
            headers = {'x-requestid': str(uuid.uuid4()),
                       "Authorization": f"Bearer {self.bearer_token}"}
            body = {"orderNumber": order_id}

            response = requests.put(url, headers=headers, json=body)
            return response.status_code
        except:
            self.l.writeLog("The function fails to connect to the API")

    def get_all_orders(self):
        """
        chana kasodh
        The function connects to the API and returns all orders from it
        :return: all orders
        """
        url = f'{self.base_url}/ordering-api/api/v1/Orders'
        orders = requests.get(url, headers=self.headers)
        return orders.json()

    def get_card_type(self):
        """
        chana kadosh
        Get the card type
        :return:
        """
        url = f"{self.base_url}/api/v1/orders/cardtypes"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def post_create_order_draft(self):
        url = f"{self.base_url}/api/v1/Orders/draft"
        body = {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 1,
                    "ProductName": ".NET Bot Black Hoodie",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 4,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        }
        response = requests.post(url, headers=self.headers, json=body)
        return response.json()



if __name__ == '__main__':
    import pprint

    api = OrderingAPI('bob', 'Pass123$')
    # api = OrderingAPI('alice', 'Pass123%24')

    pprint.pprint(api.get_order_by_id(1))


    # pprint.pprint(api.post_create_order_draft())
    # print(time.time())
    # start_time = datetime.datetime.now()  # Example start time
    # time.sleep(5)  # Sleep for 5 seconds
    # end_time = datetime.datetime.now() # Example end time
    #
    # time_diff = end_time - start_time
    #
    # print('Time difference:', time_diff.total_seconds())
