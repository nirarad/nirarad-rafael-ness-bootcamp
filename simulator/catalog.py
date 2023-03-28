import uuid
from utils.helper_functions import rabbit_mq_publish, current_time


def in_stock(order_number):
    body = {
        "OrderId": order_number,
        "Id": str(uuid.uuid4()),
        "CreationDate": current_time()
    }
    rabbit_mq_publish('OrderStockConfirmedIntegrationEvent', body)


def not_in_stock(order_number):
    body = {
        "OrderId": order_number,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": current_time()
    }
    rabbit_mq_publish('OrderStockRejectedIntegrationEvent', body)
