import json
import uuid
from datetime import datetime
from uuid import uuid4
from data_test import *
from ddt import ddt, data, unpack, file_data
import os

os.chdir(r'C:\\eshop\\Python-eshop\\rafael-ness-bootcamp\\data_test')

with open('ddt.json', 'r') as f:
    result = json.load(f)


def input_create_order(number):
    temp = result[number]
    data = {
        "UserId": temp['id'],
        "UserName": temp['UserName'],
        "OrderNumber": temp['OrderNumber'],
        "City": temp['City'],
        "Street": temp['Street'],
        "State": temp['State'],
        "Country": temp['Country'],
        "ZipCode": temp['ZipCode'],
        "CardNumber": temp['CardNumber'],
        "CardHolderName": temp['CardHolderName'],
        "CardExpiration": temp['CardExpiration'],
        "CardSecurityNumber": temp['CardSecurityNumber'],
        "CardTypeId": temp['CardTypeId'],
        "Buyer": temp['Buyer'],
        "RequestId": str(uuid.uuid4()),
        "Basket": {
           # "BuyerId": temp['Buyer'],
            "Items": [temp["items"]]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-18T14:20:24.4730559Z"
    }
    return data


def input_pyment_success(id_order):
    data = {
        "OrderId": id_order,
        "Id": str(uuid4()),
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    return data


def input_payment_failed(id_order):
    data = {
        "OrderId": id_order,
        "OrderStatus": "stockconfirmed",
        "BuyerName": "alice",
        "Id": str(uuid4()),
        "CreationDate": "2023-03-05T17:07:35.6306122Z"
    }
    return data


def input_catalog_in_stock(id_order):
    data = {
        "OrderId": id_order,
        "Id": str(uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    return data


def input_out_of_stock(id_order):
    # r = return_data()
    data = {
        "OrderId": id_order,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    return data


if __name__ == '__main__':
  pass