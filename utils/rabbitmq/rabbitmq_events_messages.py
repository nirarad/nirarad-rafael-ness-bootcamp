import json
import uuid
from utils.rabbitmq.rabbitmq_send import RabbitMQ

class SingleMessageConsumer:
    def __init__(self, queue):
        self.queue = queue
        self.mq = RabbitMQ()
        self.last_msg_method = None
        self.last_msg_body = None

    def wait_for_message(self):
        self.last_msg_method = None
        self.last_msg_body = None
        self.mq.connect()
        self.mq.consume(self.queue, self.on_message)

    def on_message(self, ch, method, properties, body):
        self.last_msg_method = method
        self.last_msg_body = json.loads(body)
        self.mq.close()

def rabbit_mq_pub(routing_key,body):
    """
    Writer:Or David
    Date:14/03/23
    Function that publish a message on RabbitMQ from its eshop_event_bus with a routing key and body
    :param routing_key: the key of the request
    :param body: body of the request
    :return: None
    """
    with RabbitMQ() as mq:
        mq.publish(exchange='eshop_event_bus',
                   routing_key=routing_key,
                   body=json.dumps(body))
def create_order():
    """
    Writer:Or David
    Date:14/03/23
    Function that publish a create order message on RabbitMQ
    :param :none
    :return: None
    """
    #b9e5dcdd-dae2-4b1c-a991-f74aae042814 instead of userID
    body = {
        "UserId": "c58a59f6-b68c-4fa9-89bc-cd7eecf959c5",
        "UserName": "alice",
        "OrderNumber": 0,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
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
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_pub('UserCheckoutAcceptedIntegrationEvent',body)
def create_order_without_items():
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a create order message on RabbitMQ with empty list of items
      :param :none
      :return: None
      """
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": 0,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_pub('UserCheckoutAcceptedIntegrationEvent',body)
def create_order_without_quantity():
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a create order message on RabbitMQ with quantity 0
      :param :none
      :return: None
      """
    body = {
        "UserId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
        "UserName": "alice",
        "OrderNumber": 0,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "b9e5dcdd-dae2-4b1c-a991-f74aae042814",
            "Items": [
                {
                    "Id": "c1f98125-a109-4840-a751-c12a77f58dff",
                    "ProductId": 1,
                    "ProductName": ".NET Bot Black Hoodie",
                    "UnitPrice": 19.5,
                    "OldUnitPrice": 0,
                    "Quantity": 0,
                    "PictureUrl": "http://host.docker.internal:5202/c/api/v1/catalog/items/1/pic/"
                }
            ]
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }
    rabbit_mq_pub('UserCheckoutAcceptedIntegrationEvent',body)
def confirm_stock(order_id):
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a confirm stock message on RabbitMQ with the id of an order
      :param order_id:an id of an order
      :return: None
      """
    body = {
          "OrderId": order_id,
          "Id": str(uuid.uuid4()),
          "CreationDate": "2023-03-05T14:52:24.705823Z"
        }
    rabbit_mq_pub('OrderStockConfirmedIntegrationEvent',body)
def reject_stock(order_id):
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a reject stock message on RabbitMQ with the id of an order
      :param order_id:an id of an order
      :return: None
      """
    body ={
        "OrderId": order_id,
        "OrderStockItems": [
            {
                "ProductId": 1,
                "HasStock": False
            }
        ],
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-05T15:51:11.5458796Z"
    }
    rabbit_mq_pub('OrderStockRejectedIntegrationEvent',body)
def change_status_awaiting_validation(order_id):
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a change status awaiting validation message on RabbitMQ with the id of an order
      :param order_id:an id of an order
      :return: None
      """
    body = {
          "OrderId": order_id,
          "OrderStatus": "awaitingvalidation",
          "BuyerName": "alice",
          "OrderStockItems": [
            {
              "ProductId": 1,
              "Units": 1
            }
          ],
          "Id": str(uuid.uuid4()),
          "CreationDate": "2023-03-05T14:27:28.8042812Z"
        }
    rabbit_mq_pub('OrderStatusChangedToAwaitingValidationIntegrationEvent', body)
def payment_succeeded(order_id):
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a payment succeeded message on RabbitMQ with the id of an order
      :param order_id:an id of an order
      :return: None
      """
    body = {
          "OrderId": order_id,
          "Id": str(uuid.uuid4()),
          "CreationDate": "2023-03-05T15:33:18.1376971Z"
        }
    rabbit_mq_pub('OrderPaymentSucceededIntegrationEvent', body)
def order_payment_failed_integration_event(order_id):
    """
      Writer:Or David
      Date:14/03/23
      Function that publish a payment falied message on RabbitMQ with the id of an order
      :param order_id:an id of an order
      :return: None
      """
    body = {
          "OrderId": order_id,
          "OrderStatus": "stockconfirmed",
          "BuyerName": "alice",
          "Id": str(uuid.uuid4()),
          "CreationDate": "2023-03-05T17:07:35.6306122Z"
        }
    rabbit_mq_pub('OrderPaymentFailedIntegrationEvent', body)
def create_new_order_bob():
    '''
    name: Or David
    date: 09/03/23
    The function create new order on rabbit with the user 'bob'
    :param none
    :return: none
    '''
    body = {
        "UserId": "c93e9a64-e4ee-42dc-a4a1-934a76b0880d",
        "UserName": "bob",
        "OrderNumber": 0,
        "City": "Redmond",
        "Street": "15703 NE 61st Ct",
        "State": "WA",
        "Country": "U.S.",
        "ZipCode": "98052",
        "CardNumber": "4012888888881881",
        "CardHolderName": "Alice Smith",
        "CardExpiration": "2024-12-31T22:00:00Z",
        "CardSecurityNumber": "123",
        "CardTypeId": 1,
        "Buyer": None,
        "RequestId": str(uuid.uuid4()),
        "Basket": {
            "BuyerId": "c93e9a64-e4ee-42dc-a4a1-934a76b0880d",
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
        },
        "Id": str(uuid.uuid4()),
        "CreationDate": "2023-03-04T14:20:24.4730559Z"
    }

    rabbit_mq_pub('UserCheckoutAcceptedIntegrationEvent',body)
