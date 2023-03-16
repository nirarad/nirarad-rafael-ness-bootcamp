import requests
from utils.api.bearer_tokenizer import BearerTokenizer


class OrderingAPI_Mocker:
    def __init__(self, username='alice', password='Pass123%24'):
        self.base_url = 'http://host.docker.internal:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.base_header = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: create_order
        Description: Function mocks Ordering API to get order by id.
        :param order_id: order id in db
        :return: order
        """
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.base_header)
        return order

    def cancel_order(self, order_id, x_requestid=None):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: create_order
        Description: Function mocks Ordering API to cancel order by id.
        :param x_requestid: unique id got in tine of order creation in Ordering service
        :param order_id: order id in db
        :return: order
        """
        headers = {**self.base_header, **{"x-requestid": str(x_requestid)}}
        json_body = {"orderNumber": order_id}
        response_status = requests.put(f'{self.base_url}/api/v1/orders/cancel', headers=headers, json=json_body)
        return response_status

    def ship_order(self, order_id, x_requestid=None):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: create_order
        Description: Function mocks Ordering API to ship order by id.
        :param x_requestid: unique id got in tine of order creation in Ordering service
        :param order_id: order id in db
        :return: order
        """
        headers = {**self.base_header, **{"x-requestid": str(x_requestid)}}
        json_body = {"orderNumber": order_id}
        response_status = requests.put(f'{self.base_url}/api/v1/orders/ship', headers=headers, json=json_body)
        return response_status


if __name__ == '__main__':
    import pprint

    api = OrderingAPI_Mocker()
    pprint.pprint(api.get_order_by_id(170).json())
    pprint.pprint(api.cancel_order(162, "eb24532a-be23-417f-b6a9-587ff9f6b845"))
    pprint.pprint(api.cancel_order(162, "eb24532a-be23-417f-b6a9-587ff9f6b845"))
