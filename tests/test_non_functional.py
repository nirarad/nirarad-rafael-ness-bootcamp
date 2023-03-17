import time
import pika
import pytest
from utils.api.ordering_api import OrderingAPI
from utils.rabbitmq.rabbitmq_utils import clear_all_queues_msg
from utils.simulators.util_funcs import status_waiting, id_waiting


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
        self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()
        # basket simulator send msg
        self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
        self.basket.consume()
        self.catalog.consume()
        # waits to get status number 2 from db
        assert status_waiting(2)
        last_id = id_waiting()
        api_with_bob = OrderingAPI(username="bob", password="Pass123%24")
        api_with_bob.cancel_order(order_id=last_id)
        if status_waiting(6) is True:
            raise AssertionError("access with bob account available, change to status 6")

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
        self.dm.stop('eshop/ordering.api:linux-latest')

        for i in range(100):
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
        self.dm.start('eshop/ordering.api:linux-latest')
        time.sleep(1)
        start_time = time.time()
        while True:
            global ord_q
            ord_q = self.rbtMQ.number_of_massages_in_queue("Ordering")
            bas_q = self.rbtMQ.number_of_massages_in_queue("Basket")
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
        self.rbtMQ.delete_msg_on_queue("Basket")
        self.rbtMQ.delete_msg_on_queue("Catalog")
        self.rbtMQ.delete_msg_on_queue("Ordering.signalrhub")
        self.dm.start('eshop/ordering.api:linux-latest')

    @pytest.mark.reliability
    def test_reliability(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders reliability by shutdown the Ordering Api service and send to it msg to continue with
         the order. the service need to continue from the last process\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        # basket simulator send msg
        self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
        self.basket.consume()
        # self.catalog.consume()
        # waits to get status number 2 from db
        if status_waiting(2) is False:
            raise ValueError("status isn't 2")
        last_id = id_waiting()

        # shutdown the ordering api, catalog send msg and tuning on ordering api
        self.dm.stop('eshop/ordering.api:linux-latest')
        self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
        self.dm.start('eshop/ordering.api:linux-latest')

        if status_waiting(3) is False:
            raise ValueError("orders don`t increase order to status 3")  # payment get msg from orders
        self.payment.consume()
        self.catalog.consume()
        if self.catalog.routing_key_catalog_get != "OrderStatusChangedToAwaitingValidationIntegrationEvent":
            raise ValueError(
                f"{self.catalog.routing_key_catalog_get} != OrderStatusChangedToAwaitingValidationIntegrationEvent")

        self.dm.start("eshop/ordering.api:linux-latest")

    @pytest.mark.reporting
    def test_reporting(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders reporting so that after avery business process the orders need to report.\n
        Date: 12/3/23\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to catch the report massage
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()
            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            time.sleep(5)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" \
                   or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "UserCheckoutAcceptedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            last_id = id_waiting()
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent" \
                   or "OrderStatusChangedToSubmittedIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "OrderStockConfirmedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            # catalog get msg from orders to check if item in stock and catalog return an answer
            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
            time.sleep(5)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToStockConfirmedIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "OrderStockConfirmedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))

            # payment send msg that paid confirmed
            self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", last_id)
            time.sleep(5)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToPaidIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "OrderStatusChangedToPaidIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            # time.sleep(10)
            # sending api request to ship order
            self.api.ship_order(last_id)
            time.sleep(10)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToShippedIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "ask to ship",
                                                self.signalrhub.routing_key_srh_get))

            # creating another order to cancel
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            time.sleep(10)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "new order: cancel",
                                                self.signalrhub.routing_key_srh_get))
            time.sleep(10)
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_reporting",
                                                "new order: cancel",
                                                self.signalrhub.routing_key_srh_get))
            last_id = id_waiting()
            cancel_status = self.api.cancel_order(last_id)
            if cancel_status == 200:
                time.sleep(10)
                self.signalrhub.consume()
                assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToCancelledIntegrationEvent"
                self.log.send(
                    self.config["TEST_PASS"].format("test_reporting",
                                                    "new order: cancel",
                                                    self.signalrhub.routing_key_srh_get))
            else:
                raise ConnectionError(f"can`t cancel with api, return {cancel_status}")

        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_reporting", "UserCheckoutAcceptedIntegrationEvent",
                                                  ae))
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_reporting", "UserCheckoutAcceptedIntegrationEvent", e))
            assert False
        finally:
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
