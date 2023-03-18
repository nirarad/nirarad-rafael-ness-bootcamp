import json
import os
import uuid


# Data getter for order in json file
class JSONDataReader(object):

    def __init__(self, filepath):
        self.items = None
        self.item = None
        self.filepath = filepath

    def get_json_order(self, order_name, order_uuid):
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
                    self.item = data[order_name]
                    if self.item is None:
                        raise Exception("Order not found.")
                    self.item['Id'] = order_uuid
                    self.item['RequestId'] = str(uuid.uuid4())
            else:
                raise Exception('Order uuid is None.')
        else:
            raise Exception('Orders JSON file path not found.')
        return self.item

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
        self.items = []
        if self.filepath is not None:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                for e in data:
                    data[e]['Id'] = str(uuid.uuid4())
                    data[e]['RequestId'] = str(uuid.uuid4())
                    self.items.append(data[e])
        else:
            raise Exception('Orders JSON file path not found.')
        if len(self.items) < 1:
            raise Exception('List of orders is empty.')
        return self.items

    def get_json_order_response(self, response_name, id_db):
        """
        Name: Artsyom Sharametsieu
        Date: 05.03.2023
        Function Name: get_json_order_response
        Description: 1.Function loads JSON ORDER DATA RESPONSES.
                     2.Searching response in json by name of response.
                     3.Inserting Request id of order in DB.
                     4.Returning full proper response.
        :param id_db: id of order in DB
        :param response_name: response name in json data
        :return: full order response message with ids
        """
        if self.filepath is not None:
            if response_name is not None:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.item = data[response_name]
                    if self.item is None:
                        raise Exception("Order not found.")
                    self.item['ordernumber'] = id_db
                    self.item['date'] = 0
            else:
                raise Exception('Response name to find is None.')
        else:
            raise Exception('Order Responses JSON file path not found.')
        return self.item


if __name__ == '__main__':
    d = JSONDataReader('../../tests/DATA/ORDERS_DATA.json')
    order = d.get_json_order('alice_normal_order', str(uuid.uuid4()))
    print(order)

