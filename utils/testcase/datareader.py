import json
import os
import uuid

from dotenv import load_dotenv


class Datareader:

    def __init__(self):
        load_dotenv('../../tests/DATA/.env.test')
        self.order = None
        self.filepath = os.getenv('ORDERS_PATH')

    def get_json_order(self, order_name, order_uuid=None):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: get_json_order
        Description: 1.Function loads JSON ORDER DATA.
                     2.Searching order in json by name of order.
                     3.Inserting Request unique id and Order unique id
                     4.Returning full proper order.
        :param order_name: name of order in json file to search
        :param order_uuid: uuid of order from outside to insert in order
        :return: full order with ids
        """
        if self.filepath is not None:
            if order_uuid is not None:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.order = data[order_name]
                    if self.order is None:
                        raise Exception("Order not found.")
                    self.order['Id'] = order_uuid
                    self.order['RequestId'] = str(uuid.uuid4())
            else:
                raise Exception('Order uuid is None.')
        else:
            raise Exception('Orders JSON file path not found.')
        return self.order


if __name__ == '__main__':
    d = Datareader()
    order = d.get_json_order('normal_alice_order', str(uuid.uuid4()))
    print(order)
