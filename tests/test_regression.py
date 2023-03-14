import time

import pytest
import requests

from utils.db.db_queries import DbQueries
from utils.simulators.util_funcs import status_waiting, id_waiting


@pytest.mark.usefixtures("setup")
class TestSanity:
    def test_submit_order(self):
        try:
            # shutdown the "background-tasks", ordering sub-service
            self.dm.containers_dict["eshop/ordering.backgroundtasks:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            time.sleep(1)
            self.basket.consume()
            # self.catalog.consume()
            # awaiting function, if there is positive results for status change on db (to number 2)
            # return True and so assertion, otherwise False
            assert status_waiting(1)
            self.log.send(
                self.config["TEST_PASS"].format("test_submit_order", "UserCheckoutAcceptedIntegrationEvent",
                                                "1"))

            assert self.basket.routing_key_basket_get == "OrderStartedIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_submit_order", "UserCheckoutAcceptedIntegrationEvent",
                                                self.basket.routing_key_basket_get))


        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_submit_order", "UserCheckoutAcceptedIntegrationEvent", ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_submit_order", "UserCheckoutAcceptedIntegrationEvent", e))

    def test_items_in_stock(self):
        try:
            # turn on the "background-tasks", ordering sub-service
            self.dm.containers_dict["eshop/ordering.backgroundtasks:linux-latest"].start()

            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            self.basket.consume()

            self.catalog.consume()
            # waits to get status number 2 from db

            assert status_waiting(2)
            last_id = id_waiting()
            # catalog get msg from orders to check if item in stock and catalog return an answer

            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id, True)
            time.sleep(2)
            assert status_waiting(3)
            self.log.send(
                self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                                "3"))
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))
            self.signalrhub.consume()
            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_items_in_stock", "UserCheckoutAcceptedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_items_in_stock", "UserCheckoutAcceptedIntegrationEvent", e))

    def test_items_not_in_stock(self):
        try:

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            self.basket.consume()
            self.catalog.consume()

            # waits to get status number 2 from db
            assert status_waiting(2)
            last_id = id_waiting()
            # catalog get msg from orders to check if item in stock and catalog return an answer

            self.catalog.send_to_queue(routing_key="OrderStockRejectedIntegrationEvent", order_id=last_id)
            time.sleep(2)
            assert status_waiting(6)
            self.log.send(
                self.config["TEST_PASS"].format("test_items_not_in_stock", "OrderStockRejectedIntegrationEvent",
                                                "6"))

        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_items_not_in_stock", "OrderStockRejectedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_items_not_in_stock", "OrderStockRejectedIntegrationEvent", e))

    def test_payment_success(self):
        try:
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            # OrderStartedIntegrationEvent
            self.basket.consume()
            self.catalog.consume()
            # OrderStatusChangedToSubmittedIntegrationEvent
            self.signalrhub.consume()

            # waits to get status number 2 from db
            assert status_waiting(2)
            last_id = id_waiting()

            # catalog get msg from orders to check if item in stock and catalog return an answer
            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
            time.sleep(30)
            #  OrderStatusChangedToAwaitingValidationIntegrationEvent
            self.signalrhub.consume()
            # awaiting to status 3
            assert status_waiting(3)
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_success", "OrderStockConfirmedIntegrationEvent",
                                                "3"))
            # assert that catalog get massage from orders
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_success", "OrderStockConfirmedIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_success", "OrderStatusChangedToSubmittedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))

            # OrderStatusChangedToStockConfirmedIntegrationEvent
            self.payment.consume()
            self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(4)
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_success", "OrderPaymentSucceededIntegrationEvent",
                                                "4"))
            # OrderStatusChangedToPaidIntegrationEvent
            self.catalog.consume()
            # OrderStatusChangedToPaidIntegrationEvent
            self.signalrhub.consume()
            # turn on back the "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_payment_success", "OrderStockRejectedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_payment_success", "OrderStockRejectedIntegrationEvent", e))

    def test_payment_failed(self):
        try:
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            # OrderStartedIntegrationEvent
            self.basket.consume()
            self.catalog.consume()
            # OrderStatusChangedToSubmittedIntegrationEvent
            self.signalrhub.consume()

            # waits to get status number 2 from db
            assert status_waiting(2)
            last_id = id_waiting()

            # catalog get msg from orders to check if item in stock and catalog return an answer
            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
            time.sleep(30)
            #  OrderStatusChangedToAwaitingValidationIntegrationEvent
            self.signalrhub.consume()
            # awaiting to status 3
            assert status_waiting(3)
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_failed", "OrderStockConfirmedIntegrationEvent",
                                                "3"))
            # assert that catalog get massage from orders
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_failed", "OrderStockConfirmedIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_failed", "OrderStatusChangedToSubmittedIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))

            # OrderStatusChangedToStockConfirmedIntegrationEvent
            self.payment.consume()
            self.payment.send_to_queue("OrderPaymentFailedIntegrationEvent", last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(6)
            self.log.send(
                self.config["TEST_PASS"].format("test_payment_failed", "OrderPaymentFailedIntegrationEvent",
                                                "6"))
            # OrderStatusChangedToCancelledIntegrationEvent
            self.signalrhub.consume()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_payment_failed", "OrderPaymentFailedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_payment_failed", "OrderPaymentFailedIntegrationEvent", e))

    def test_cancel_after_submitted(self):
        try:
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            # OrderStartedIntegrationEvent
            self.basket.consume()
            self.catalog.consume()
            # OrderStatusChangedToSubmittedIntegrationEvent
            self.signalrhub.consume()

            # waits to get status number 2 from db
            assert status_waiting(2)
            last_id = id_waiting()
            self.api.cancel_order(order_id=last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(6)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_submitted", "UserCheckoutAcceptedIntegrationEvent",
                                                "6"))
            # turn on back "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()

        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_cancel_after_submitted", "UserCheckoutAcceptedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_cancel_after_submitted", "UserCheckoutAcceptedIntegrationEvent", e))

    def test_cancel_on_stock_confirmed(self):
        try:
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()

            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            # OrderStartedIntegrationEvent
            self.basket.consume()
            # OrderStatusChangedToAwaitingValidationIntegrationEvent
            self.catalog.consume()
            # OrderStatusChangedToSubmittedIntegrationEvent
            self.signalrhub.consume()

            # waits to get status number 2 from db
            assert status_waiting(2)
            last_id = id_waiting()

            # catalog get msg from orders to check if item in stock and catalog return an answer
            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
            time.sleep(30)
            #  OrderStatusChangedToAwaitingValidationIntegrationEvent
            self.signalrhub.consume()
            # awaiting to status 3
            assert status_waiting(3)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent",
                                                "3"))
            # assert that catalog get massage from orders
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))

            # OrderStatusChangedToStockConfirmedIntegrationEvent
            self.api.cancel_order(order_id=last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(6)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent",
                                                "6"))
            # turn on back "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent",
                                                  ae))
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent", e))
