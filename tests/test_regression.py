import time

import pytest
import requests

from utils.api.ordering_api import OrderingAPI
from utils.db.db_queries import DbQueries
from utils.rabbitmq.rabbitmq_utils import clear_all_queues_msg
from utils.simulators.util_funcs import status_waiting, id_waiting


@pytest.mark.usefixtures("setup")
class TestRegression:
    """
    Name: menahem rotblat.\n
    Description: class contain the main tests regression Test Cases,
    the test cases covered the base functionality of the mss,
    main success scenario, canceling and updating order.
    in payment and catalog we have been split tests on the paid confirmed or not on payment
    and also in catalog in case that stock confirmed or not.\n
    Date: 12/3/23.\n
    """
    @pytest.mark.submit_order
    def test_submit_order(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss submit sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_submit_order", "UserCheckoutAcceptedIntegrationEvent", e))
            assert False
        finally:
            # turn on the "background-tasks", ordering sub-service
            self.dm.containers_dict["eshop/ordering.backgroundtasks:linux-latest"].start()

    @pytest.mark.items_in_stock
    def test_items_in_stock(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss items in stock sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
            # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept massage logs from orders
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].stop()
            # basket simulator send msg
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            self.basket.consume()
            self.signalrhub.consume()
            self.catalog.consume()
            # waits to get status number 2 from db

            assert status_waiting(2)
            last_id = id_waiting()
            # catalog get msg from orders to check if item in stock and catalog return an answer

            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", last_id)
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_items_in_stock", "UserCheckoutAcceptedIntegrationEvent", e))
            assert False

    @pytest.mark.items_not__in_stock
    def test_items_not_in_stock(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss items not stock sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_items_not_in_stock", "OrderStockRejectedIntegrationEvent", e))
            assert False

    @pytest.mark.payment_success
    def test_payment_success(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment successful sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(2)
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_payment_success", "OrderStockRejectedIntegrationEvent", e))
            assert False

    @pytest.mark.payment_failed
    def test_payment_failed(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment failed sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_payment_failed", "OrderPaymentFailedIntegrationEvent", e))
            assert False

    @pytest.mark.cancel_after_submitted
    def test_cancel_after_submitted(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment failed sub-scenario.\n
        Date: 12/3/23.\n
        """
        try:
            time.sleep(5)
            clear_all_queues_msg()
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
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_cancel_after_submitted", "UserCheckoutAcceptedIntegrationEvent",
                                                e))
            assert False

    @pytest.mark.cancel_on_stock_confirmed
    def test_cancel_on_stock_confirmed(self):
        """
        Name: menahem rotblat\n
        Description: tests cancel order after status have been 2 the status should change to 6 (canceled) .\n
        Date: 12/3/23\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
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
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed",
                                                "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed",
                                                "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))

            # OrderStatusChangedToStockConfirmedIntegrationEvent

            self.api.cancel_order(order_id=last_id)
            time.sleep(30)
            # awaiting to status 6
            assert status_waiting(6)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent",
                                                "6"))
            # turn on back "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_cancel_on_stock_confirmed",
                                                  "OrderStockConfirmedIntegrationEvent",
                                                  ae))
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_cancel_on_stock_confirmed", "OrderStockConfirmedIntegrationEvent",
                                                e))
            assert False

    @pytest.mark.cancel_after_paid
    def test_cancel_after_paid(self):
        """
        Name: menahem rotblat.\n
        Description: tests cancel order after status have been 3 the status should not change to 6 (canceled)
        and need to stay in same status.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
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
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "OrderStockConfirmedIntegrationEvent",
                                                "3"))
            # assert that catalog get massage from orders
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            self.payment.consume()
            self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(4)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_paid", "OrderPaymentSucceededIntegrationEvent",
                                                "4"))
            # OrderStatusChangedToPaidIntegrationEvent
            self.catalog.consume()

            # OrderStatusChangedToStockConfirmedIntegrationEvent
            self.api.cancel_order(order_id=last_id)
            time.sleep(30)
            # awaiting to status not change to 6 and is staying 4
            assert status_waiting(4)
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "OrderPaymentSucceededIntegrationEvent",
                                                "4"))
            # turn on back "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_cancel_after_paid",
                                                  "OrderPaymentSucceededIntegrationEvent",
                                                  ae))
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_cancel_after_paid",
                                                "OrderPaymentSucceededIntegrationEvent", e))
            assert False

    @pytest.mark.update_to_shipped
    def test_update_to_shipped(self):
        """
        Name: menahem rotblat.\n
        Description: tests updating order status to "shipped" the status should change to 5.\n
        Date: 12/3/23.\n
        """
        try:
            clear_all_queues_msg()
            time.sleep(5)
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
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "test_update_to_shiped",
                                                "3"))
            # assert that catalog get massage from orders
            assert self.catalog.routing_key_catalog_get == "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_cancel_after_paid",
                                                "test_update_to_shiped",
                                                self.catalog.routing_key_catalog_get))

            assert self.signalrhub.routing_key_srh_get == "OrderStatusChangedToSubmittedIntegrationEvent" or "OrderStatusChangedToAwaitingValidationIntegrationEvent"
            self.log.send(
                self.config["TEST_PASS"].format("test_update_to_shiped",
                                                "OrderStatusChangedToAwaitingValidationIntegrationEvent",
                                                self.signalrhub.routing_key_srh_get))
            self.payment.consume()
            self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", last_id)
            time.sleep(30)
            # awaiting to status 4
            assert status_waiting(4)
            self.log.send(
                self.config["TEST_PASS"].format("test_update_to_shiped", "OrderPaymentSucceededIntegrationEvent",
                                                "4"))
            # OrderStatusChangedToPaidIntegrationEvent
            self.catalog.consume()

            # OrderStatusChangedToStockConfirmedIntegrationEvent
            self.api.ship_order(order_id=last_id)
            time.sleep(30)
            # awaiting to status not change and is 4
            assert status_waiting(5)
            self.log.send(
                self.config["TEST_PASS"].format("test_update_to_shiped",
                                                "OrderPaymentSucceededIntegrationEvent",
                                                "5"))
            # turn on back "ordering-signalrhub-1" service
            self.dm.containers_dict["eshop/ordering.signalrhub:linux-latest"].start()
        except AssertionError as ae:
            self.log.send(
                self.config["ASSERT_FAIL"].format("test_update_to_shiped",
                                                  "OrderPaymentSucceededIntegrationEvent",
                                                  ae))
            assert False
        except Exception as e:
            self.log.send(
                self.config["TEST_FAIL"].format("test_update_to_shiped",
                                                "OrderPaymentSucceededIntegrationEvent", e))
            assert False
