import json
import uuid
import requests
from utils.rabbitmq.rabbitmq_receive import *
from utils.db.db_utils import MSSQLConnector
from utils.rabbitmq.rabbit_messages import RabbitMessages

usercheckout=os.getenv('USERCHECKOUT')
exchange=os.getenv('EXCHANGE')
instock=os.getenv('STOCKCONFIRMERD')
stockreject=os.getenv('STOCKREJECT')
paymentfail=os.getenv('PAYMENTFAIL')
paymentsucceeded=os.getenv('PAYMENTSUCCEEDED')


class BasketApi:
    def submmit(self):
        with RabbitMQ() as mq:
            with MSSQLConnector() as conn:
                mq.publish(exchange=exchange, routing_key=usercheckout, body=json.dumps(body))
                docker.start('eshop/ordering.api:linux-latest')
