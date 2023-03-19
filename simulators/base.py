import time
from utils.rabbitmq.rabbitmq_receive import *
from utils.rabbitmq.rabbitmq_send import *
from log.logger import Log
from data_test.massege import *
import json


class Base(object):
    def __init__(self, queue):
        self.l = Log()
        # Each creation appears from one of its successors, base receives the queue name
        self.queue = queue

    def Receives_a_routing_key_to_rabbitMQ(self, routing_key, idO):
        """
        writer: chana kadosh
        A function that sends messages to the MQ bit

        Description: The function receives from its successors the following data: routing_key and ID,
        and according to the routing key it enters the correct DATA into the publish function
        of the rabbitMQ class.
        If the call fails: the function writes the error to the log
        """
        try:

            match routing_key:
                case 'UserCheckoutAcceptedIntegrationEvent':
                    temp = input_create_order(idO)
                case 'OrderStockConfirmedIntegrationEvent':
                    temp = input_catalog_in_stock(idO)
                case 'OrderPaymentSucceededIntegrationEvent':
                    temp = input_pyment_success(idO)
                case 'OrderStockRejectedIntegrationEvent':
                    temp = input_out_of_stock(idO)
                case 'OrderPaymentFailedIntegrationEvent':
                    temp = input_payment_failed(idO)

            with RabbitMQ() as mq:
                mq.publish(exchange='eshop_event_bus',
                           routing_key=routing_key,
                           body=json.dumps(temp))
        except Exception as e:
            self.l.writeLog(
                f"Failed in-Receives_a_routing_key_and_transfers_to_rabbitMQ function,parameter: "
                f"routing_key:{routing_key}  {e}")
            raise Exception(f"Failed in-Receives_a_routing_key_and_transfers_to_rabbitMQ function,parameter: "
                            f"routing_key:{routing_key}  {e}")

    def Messages_that_rabbitMQ_receives(self):
        """
        writer: chana kadosh
        Description: The function listens to messages that enter rabbitMQ,
        This function should get the queue name it should listen.
        """
        try:
            with RabbitMQ() as mq:
                # Connect to rabbitMQ
                mq.connect()
                # Sending to the consume function, receives the queue name and the callback function.
                mq.consume(self.queue, callback)
                # Emptying the queue
                # mq.purge_queue()
        except Exception as e:
            self.l.writeLog(f"Failed in-Messages_that_rabbitMQ_receives function,"
                            f" parameter: queue:{self.queue} {e}")
            raise Exception(f"Failed in-Messages_that_rabbitMQ_receives function,"
                            f" parameter: queue:{self.queue} {e}")

    def waiting_for_an_update(self, Estatus, db):
        """
        chani kadosh
        The function receives the status to which the order should change, and it waits until the status of the order equals the status it received.
        Maximum waiting time up to 100 seconds.
        :param Estatus: The status to which the order should change.
        :param db: An instance of a DB.
        :return:
        """
        status = 0
        count = 0
        try:
            # Loop, until status becomes Estatus
            while status != Estatus:
                if count < 100:
                    time.sleep(1)
                    result_id = db.select_query('SELECT * FROM ordering.orders WHERE id = (SELECT MAX(id) FROM '
                                                'ordering.orders)')
                    status = result_id[0]['OrderStatusId']
                    count += 1
                else:
                    break
            return status
        except Exception as e:
            self.l.writeLog(f"Failed in-waiting_for_an_update function,parameter: {Estatus}!={status} {e}")
            raise Exception(f"Failed in-waiting_for_an_update function,parameter: {Estatus}!={status} {e}")

