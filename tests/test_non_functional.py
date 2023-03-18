import time
import pika
import pytest
from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_utils import clear_all_queues_msg
from utils.simulators.util_funcs import status_waiting, id_waiting
from data import config


@pytest.mark.usefixtures("setup")
class TestNonFunc:
    @pytest.mark.security
    def test_security(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders security by send new order with alice userID,
         after that, try to change the status order to cancel with bob userID.
         the order status should not change\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept massage logs from orders
        self.dm.stop(config.containers["signalrhub"])
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        self.catalog.consume()
        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()
        api_with_bob = OrderingAPI(username=self.config["BOB_NAME"], password=self.config["BOB_PASS"])
        api_with_bob.cancel_order(order_id=last_id)
        if status_waiting(self.config["CANCELLED"]) is True:
            raise AssertionError(self.config["BOB_ERROR"])

    @pytest.mark.scalability
    def test_scalability(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders scalability by shut down the Ordering Api service and send to it 100 messages
         after that turn orders on and the service need to get them all and process
          so the Basket service also get 100 messages\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        self.dm.stop(config.containers["ordering_api"])

        for i in range(100):
            self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.dm.start(config.containers["ordering_api"])
        time.sleep(1)
        start_time = time.time()
        while True:
            global ord_q
            ord_q = self.rbtMQ.number_of_massages_in_queue(config.queues["ordering"])
            bas_q = self.rbtMQ.number_of_massages_in_queue(config.queues["basket"])
            end_time = time.time()
            elapsed_time = end_time - start_time
            global hours
            hours = int(elapsed_time / 3600)
            minutes = int(elapsed_time / 60)
            if ord_q <= 0 and bas_q >= 100:
                try:
                    assert True
                    self.log.send(
                        self.config["TEST_PASS"].format("test_scalability",
                                                        f"msg in Ordering queue: {ord_q} and Basket queue {bas_q}, ",
                                                        f"Test took {hours} hours, {minutes} minute(s) and {elapsed_time % 60:.2f} seconds."))
                    self.rbtMQ.close()
                    break
                except pika.exceptions.ChannelClosed as e:
                    self.log.send(
                        self.config["TEST_FAIL"].format("test_scalability", "while loop",
                                                        e))
            if hours > 1 and ord_q > 0:
                raise AssertionError(f"over then {hours} and still there {ord_q} messages")
        self.rbtMQ.delete_msg_on_queue(config.queues["basket"])
        self.rbtMQ.delete_msg_on_queue(config.queues["catalog"])
        self.rbtMQ.delete_msg_on_queue(config.queues["signalrhub"])
        self.dm.start(config.containers["ordering_api"])

    @pytest.mark.reliability
    def test_reliability(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders reliability by shutdown the Ordering Api service and send to it msg to continue with
         the order. the service need to continue from the last process\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        self.dm.start(config.containers["ordering_api"])
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        # self.catalog.consume()
        # waits to get status number 2 from db
        if status_waiting(self.config["SUBMITTED"]) is False:
            raise ValueError(self.config["VALUE_ERROR"].format("status isn't 2"))
        last_id = id_waiting()

        # shutdown the ordering api, catalog send msg and tuning on ordering api
        self.dm.stop(config.containers["ordering_api"])
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        self.dm.start(config.containers["ordering_api"])

        if status_waiting(self.config["STOCK_CONFIRMED"]) is False:
            raise ValueError(self.config["VALUE_ERROR"].format("orders don`t increase order status to 3"))  # payment get msg from orders
        self.payment.consume()
        self.catalog.consume()
        if self.catalog.routing_key_catalog_get != config.r_key["receive"]["catalog"]:
            raise ValueError(
                f"{self.catalog.routing_key_catalog_get} != OrderStatusChangedToAwaitingValidationIntegrationEvent")

        self.dm.start(config.containers["ordering_api"])

    @pytest.mark.reporting
    def test_reporting(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders reporting so that after avery business process the orders need to report.\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to catch the report massage
        self.dm.containers_dict[config.containers["signalrhub"]].stop()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"]\
               or config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_reporting",
                                            "UserCheckoutAcceptedIntegrationEvent",
                                            self.signalrhub.routing_key_srh_get))
        last_id = id_waiting()
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] \
               or config.r_key["receive"]["signalrhub"]["waiting"]
        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        time.sleep(5)
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["stock_confirmed"]

        # payment send msg that paid confirmed
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"], last_id)
        time.sleep(5)
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["paid"]
        # time.sleep(10)
        # sending api request to ship order
        self.api.ship_order(last_id)
        time.sleep(10)
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["shipped"]

        # creating another order to cancel
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        time.sleep(10)
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"]

        time.sleep(10)
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["waiting"]

        last_id = id_waiting()
        cancel_status = self.api.cancel_order(last_id)
        if cancel_status == 200:
            time.sleep(10)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["cancelled"]
        else:
            raise ConnectionError(f"can`t cancel with api, return {cancel_status}")
        self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
