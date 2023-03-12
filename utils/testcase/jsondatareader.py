import json
import os
import pprint
import uuid

from dotenv import load_dotenv


class JSONDataReader(object):
    # Data getter for order in json file
    load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')

    def __init__(self):
        self.orders = None
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

    def get_json_all_orders(self):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: get_json_order
        Description: 1.Function loads JSON ORDER DATA.
                     2.Searching order for all orders.
                     3.Inserting in order unique id and Order unique id
                     4.Returning full proper orders.
        :return: full order with ids
        """
        self.orders = []
        if self.filepath is not None:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                for e in data:
                    data[e]['Id'] = str(uuid.uuid4())
                    data[e]['RequestId'] = str(uuid.uuid4())
                    self.orders.append(data[e])
        else:
            raise Exception('Orders JSON file path not found.')
        if len(self.orders) < 1:
            raise Exception('List of orders is empty.')
        return self.orders


if __name__ == '__main__':
    d = JSONDataReader()
    # order = d.get_json_order('alice_normal_order', str(uuid.uuid4()))
    # print(order)
    orders = d.get_json_all_orders()
    pprint.pp(orders)
