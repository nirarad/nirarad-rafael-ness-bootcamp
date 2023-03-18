import time
from pprint import pprint
import pytest

from data import config
from utils.rabbitmq.rabbitmq_utils import clear_all_queues_msg
from utils.simulators.util_funcs import status_waiting, id_waiting


@pytest.mark.usefixtures("setup")
class TestSanity:

    @pytest.mark.api_test
    def test_api(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders api's, on the way we nees to change the order status
        for the next test, so we use with all simulators, like payment for example
        because we need to raise the order status to 4 (payment status), then we change it to 5 (shipped)\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        # creating new order
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        self.catalog.consume()
        # get the OrderStatusId how just created
        id_under_test = id_waiting()

        #  get all orders
        all_orders = self.api.get_orders()
        assert all_orders.status_code == self.config["SUCCESS"]
        self.log.send(self.config["TEST_PASS"].format("test_api", "get_orders", all_orders))

        #  get order by id
        res = self.api.get_order_by_id(id_under_test)
        assert res.status_code == self.config["SUCCESS"]
        self.log.send(self.config["TEST_PASS"].format("test_api", "get_order_by_id", res))

        # get card types from db
        res = self.api.get_cardtypes()
        assert res.status_code == self.config["SUCCESS"]
        self.log.send(self.config["TEST_PASS"].format("test_api", "get_cardtypes", res))
        # move the item to "item in stock => id = 3"
        self.catalog.send_to_queue(
            self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], id_under_test))
        # move the item to "payment succeeded" => id = 4"
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"], id_under_test)
        #  move the item to "shipped" => id = 5"
        res = self.api.ship_order(id_under_test)
        assert res.status_code == self.config["SUCCESS"]
        self.log.send(self.config["TEST_PASS"].format("test_api", "ship_order", res))

        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        id_cancel_test = id_waiting()
        self.basket.consume()
        # move item to "cancel order" => id = 6"
        #  we can only do it with OrderStatusId is between 1-3
        res = self.api.cancel_order(id_cancel_test)
        assert res == self.config["SUCCESS"]
        self.log.send(self.config["TEST_PASS"].format("test_api", "cancel_order", res))

    @pytest.mark.mss
    def test_successful_flow_mss(self):
        """
        Name: menahem rotblat.\n
        Description: tests Orders flow (successfully) mss. so in the end DB contain order
        with the field - OrderStatusId with status 4 (paid) \n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        self.dm.containers_dict[config.containers["signalrhub"]].stop()
        # creating new order => basket simulator send msg. status need to be: 1 and then 2
        self.basket.send_to_queue(config.r_key["sending"]["basket"])  # OrderStartedIntegrationEvent
        self.basket.consume()
        self.catalog.consume()
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        # awaiting function, if there is positive results for status change on db (to number 2)
        # return True and so assertion, otherwise False
        assert status_waiting(self.config["SUBMITTED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_successful_flow_mms", "UserCheckoutAcceptedIntegrationEvent",
                                            f"status: {self.config['SUBMITTED']}"))
        #  catalog approve that item in stock => catalog simulator send msg. status need to be: 3

        last_id = id_waiting()
        self.catalog.send_to_queue(self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id))
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_successful_flow_mms", "OrderStockConfirmedIntegrationEvent",
                                            f"status: {self.config['STOCK_CONFIRMED']}"))
        #  payment approve that item paid => payment simulator send msg. status need to be: 4

        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["stock_confirmed"]
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"], last_id)
        assert status_waiting(self.config["PAID"])
        self.log.send(
            self.config["TEST_PASS"].format("test_successful_flow_mms", "OrderPaymentSucceededIntegrationEvent",
                                            f"status: {self.config['PAID']}"))
        # orders send a message to catalog, payment and webhook that paid confirmed, we consume
        # them (except webhook)

        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["paid"]
        self.catalog.consume()
        self.dm.containers_dict[config.containers["signalrhub"]].start()
