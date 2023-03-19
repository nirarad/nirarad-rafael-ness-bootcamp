import time
import pytest
from numpy.distutils.command.config import config

from data import config
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
        clear_all_queues_msg()
        # shutdown the "background-tasks", ordering sub-service
        self.dm.containers_dict[config.containers["ordering_bg"]].stop()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        # awaiting function, if there is positive results for status change on db (to number 2)
        # return True and so assertion, otherwise False
        if status_waiting(self.config["AWAITING_VALIDATION"]) is False:
            raise ValueError(self.config["VALUE_ERROR"].format("status not increased to 2"))

        assert self.basket.routing_key_basket_get == config.r_key["receive"]["basket"]
        # turn on the "background-tasks", ordering sub-service
        self.dm.containers_dict[config.containers["ordering_bg"]].start()

    @pytest.mark.items_in_stock
    def test_items_in_stock(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss items in stock sub-scenario.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        self.signalrhub.consume()
        self.catalog.consume()
        # waits to get status number 2 from db

        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()
        # catalog get msg from orders to check if item in stock and catalog return an answer

        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                            "3"))
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                            self.catalog.routing_key_catalog_get))
        self.signalrhub.consume()
        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_items_in_stock", "OrderStockConfirmedIntegrationEvent",
                                            self.signalrhub.routing_key_srh_get))
        self.dm.containers_dict[config.containers["signalrhub"]].start()

    @pytest.mark.items_not__in_stock
    def test_items_not_in_stock(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss items not stock sub-scenario.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        self.basket.consume()
        self.catalog.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()
        # catalog get msg from orders to check if item in stock and catalog return an answer

        self.catalog.send_to_queue(routing_key=config.r_key["sending"]["catalog"]["rejected"], order_id=last_id)
        assert status_waiting(self.config["CANCELLED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_items_not_in_stock", config.r_key["sending"]["catalog"]["rejected"],
                                            self.config["CANCELLED"]))

    @pytest.mark.payment_success
    def test_payment_success(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment successful sub-scenario.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        # OrderStartedIntegrationEvent
        self.basket.consume()
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 - submitted, from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()

        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        #  OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.signalrhub.consume()
        # awaiting to status 3 - stockConfirmed
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_success", config.r_key["sending"]["catalog"]["confirmed"],
                                            "3"))
        # assert that catalog get massage from orders
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_success", config.r_key["receive"]["catalog"],
                                            self.catalog.routing_key_catalog_get))

        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_success", config.r_key["receive"]["signalrhub"]["submit"],
                                            self.signalrhub.routing_key_srh_get))

        # OrderStatusChangedToStockConfirmedIntegrationEvent
        self.payment.consume()
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"], last_id)
        # awaiting to status 4
        assert status_waiting(self.config["PAID"])
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_success", config.r_key["sending"]["payment"]["succeeded"],
                                            self.config["PAID"]))
        # OrderStatusChangedToPaidIntegrationEvent
        self.catalog.consume()
        # OrderStatusChangedToPaidIntegrationEvent
        self.signalrhub.consume()
        # turn on back the "ordering-signalrhub-1" service
        self.dm.containers_dict[config.containers["signalrhub"]].start()

    @pytest.mark.payment_failed
    def test_payment_failed(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment failed sub-scenario.\n
        Date: 12/3/23.\n
        """

        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()

        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        # OrderStartedIntegrationEvent
        self.basket.consume()
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()

        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)

        #  OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.signalrhub.consume()
        # awaiting to status 3
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_failed", config.r_key["sending"]["catalog"]["confirmed"],
                                            self.config["STOCK_CONFIRMED"]))
        # assert that catalog get massage from orders
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_failed", config.r_key["sending"]["catalog"]["confirmed"],
                                            self.catalog.routing_key_catalog_get))

        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_failed", config.r_key["receive"]["signalrhub"]["submit"],
                                            self.signalrhub.routing_key_srh_get))

        # OrderStatusChangedToStockConfirmedIntegrationEvent
        self.payment.consume()
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["failed"], last_id)
        # awaiting to status 4
        assert status_waiting(self.config["CANCELLED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_payment_failed", config.r_key["sending"]["payment"]["failed"],
                                            self.config["CANCELLED"]))
        # OrderStatusChangedToCancelledIntegrationEvent
        self.signalrhub.consume()

    @pytest.mark.cancel_after_submitted
    def test_cancel_after_submitted(self):
        """
        Name: menahem rotblat.\n
        Description: tests mss payment failed sub-scenario.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()

        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        # OrderStartedIntegrationEvent
        self.basket.consume()
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()
        self.api.cancel_order(order_id=last_id)
        # awaiting to status 4
        assert status_waiting(self.config["CANCELLED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_submitted", last_id,
                                            self.config["CANCELLED"]))
        # turn on back "ordering-signalrhub-1" service
        self.dm.containers_dict[config.containers["signalrhub"]].start()

    @pytest.mark.cancel_on_stock_confirmed
    def test_cancel_on_stock_confirmed(self):
        """
        Name: menahem rotblat\n
        Description: tests cancel order after status have been 2 the status should change to 6 (canceled) .\n
        Date: 12/3/23\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()

        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        # OrderStartedIntegrationEvent
        self.basket.consume()
        # OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()

        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"],last_id)
        #  OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.signalrhub.consume()
        # awaiting to status 3
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            self.config["STOCK_CONFIRMED"]))
        # assert that catalog get massage from orders
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            config.r_key["receive"]["catalog"]))

        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            config.r_key["receive"]["signalrhub"]["submit"]))

        # OrderStatusChangedToStockConfirmedIntegrationEvent

        self.api.cancel_order(order_id=last_id)
        # awaiting to status 6
        assert status_waiting(self.config["CANCELLED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_on_stock_confirmed", config.r_key["receive"]["catalog"],
                                            self.config["CANCELLED"]))
        # turn on back "ordering-signalrhub-1" service
        self.dm.containers_dict[config.containers["signalrhub"]].start()

    @pytest.mark.cancel_after_paid
    def test_cancel_after_paid(self):
        """
        Name: menahem rotblat.\n
        Description: tests cancel order after status have been 3 the status should not change to 6 (canceled)
        and need to stay in same status.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()
        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])
        # OrderStartedIntegrationEvent
        self.basket.consume()
        # OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()

        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        #  OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.signalrhub.consume()
        # awaiting to status 3
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            self.config["STOCK_CONFIRMED"]))
        # assert that catalog get massage from orders
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            config.r_key["receive"]["catalog"]))

        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["receive"]["catalog"],
                                            config.r_key["receive"]["signalrhub"]["waiting"]))
        self.payment.consume()
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"], last_id)
        # awaiting to status 4
        assert status_waiting(self.config["PAID"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid", "OrderPaymentSucceededIntegrationEvent",
                                            "4"))
        # OrderStatusChangedToPaidIntegrationEvent
        self.catalog.consume()

        # OrderStatusChangedToStockConfirmedIntegrationEvent
        self.api.cancel_order(order_id=last_id)
        # awaiting to status not change to 6 and is staying on 4
        assert status_waiting(self.config["PAID"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["sending"]["payment"]["succeeded"],
                                            self.config["PAID"]))
        # turn on back "ordering-signalrhub-1" service
        self.dm.containers_dict[config.containers["signalrhub"]].start()

    @pytest.mark.update_to_shipped
    def test_update_to_shipped(self):
        """
        Name: menahem rotblat.\n
        Description: tests updating order status to "shipped" the status should change to 5.\n
        Date: 12/3/23.\n
        """
        clear_all_queues_msg()
        # shutdown the "ordering-signalrhub-1", ordering sub-service, to accept the massage logs from orders
        self.dm.containers_dict[config.containers["signalrhub"]].stop()

        # basket simulator send msg
        self.basket.send_to_queue(config.r_key["sending"]["basket"])  # OrderStartedIntegrationEvent
        self.basket.consume()
        # OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.catalog.consume()
        # OrderStatusChangedToSubmittedIntegrationEvent
        self.signalrhub.consume()

        # waits to get status number 2 from db
        assert status_waiting(self.config["SUBMITTED"])
        last_id = id_waiting()

        # catalog get msg from orders to check if item in stock and catalog return an answer
        self.catalog.send_to_queue(config.r_key["sending"]["catalog"]["confirmed"], last_id)
        #  OrderStatusChangedToAwaitingValidationIntegrationEvent
        self.signalrhub.consume()
        # awaiting to status 3
        assert status_waiting(self.config["STOCK_CONFIRMED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            self.config["STOCK_CONFIRMED"]))
        # assert that catalog get massage from orders
        assert self.catalog.routing_key_catalog_get == config.r_key["receive"]["catalog"]
        self.log.send(
            self.config["TEST_PASS"].format("test_cancel_after_paid",
                                            config.r_key["sending"]["catalog"]["confirmed"],
                                            config.r_key["receive"]["catalog"]))

        assert self.signalrhub.routing_key_srh_get == config.r_key["receive"]["signalrhub"]["submit"] or \
               config.r_key["receive"]["signalrhub"]["waiting"]
        self.log.send(
            self.config["TEST_PASS"].format("test_update_to_shiped",
                                            config.r_key["receive"]["catalog"],
                                            config.r_key["receive"]["signalrhub"]["waiting"]))
        self.payment.consume()
        self.payment.send_to_queue(config.r_key["sending"]["payment"]["succeeded"],last_id)
        # awaiting to status 4
        assert status_waiting(self.config["PAID"])
        self.log.send(
            self.config["TEST_PASS"].format("test_update_to_shiped", config.r_key["sending"]["payment"]["succeeded"],
                                            self.config["PAID"]))
        # OrderStatusChangedToPaidIntegrationEvent
        self.catalog.consume()

        # OrderStatusChangedToStockConfirmedIntegrationEvent
        self.api.ship_order(order_id=last_id)
        # awaiting to status not change and is 4
        assert status_waiting(self.config["SHIPPED"])
        self.log.send(
            self.config["TEST_PASS"].format("test_update_to_shiped",
                                            config.r_key["sending"]["payment"]["succeeded"],
                                            self.config["SHIPPED"]))
        # turn on back "ordering-signalrhub-1" service
        self.dm.containers_dict[config.containers["signalrhub"]].start()
