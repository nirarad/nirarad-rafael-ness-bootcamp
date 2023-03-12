import json
import uuid
import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.body = None

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def update5(self,order_id):
        auto=self.headers
        headers = {
                    'Authorization':f'Bearer {BearerTokenizer().bearer_token}',
                    'Content-Type': 'application/json',
                    'x-requestid': str(uuid.uuid4())
                  }
        print(headers)
        #self.headers['Content-Type'] = 'application/json'
        #self.headers['x-requestid'] = str(uuid.uuid4())
        print(self.headers)
        endpoint = f'{self.base_url}/ordering-api/api/v1/Orders/ship'
        self.body = {"orderNumber": order_id}
        print(self.body)
        requests.put(url=endpoint, data=json.dumps(self.body),headers=headers)

        # self.headers['Content-Type'] = 'application/json'
        # self.headers['x-requestid'] = str(uuid.uuid4())
        # if not str(order_id).isnumeric():
        #     raise ValueError("order id have to be a number")
        # try:
        #     endpoint = f'{self.base_url}/ordering-api/api/v1/Orders/ship'
        #     self.body = {"orderNumber": order_id}
        #     response = requests.put(url=endpoint, data=json.dumps(self.body), headers=self.headers)
        # except requests.exceptions.RequestException as e:
        #     raise SystemExit(e)
        # return response


        # body = "{" \
        #         "\"orderNumber\": " +order_id+ \
        #         "}"
        #requests.put('http://host.docker.internal:5102/ordering-api/api/v1/Orders/ship',data=json.dumps(body),headers=headers)


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.get_order_by_id(21).json())
    api.update5(28)

