import logging
import time
from pprint import pprint
import pytest
import requests

from utils.db.db_queries import DbQueries
from utils.simulators.util_funcs import status_waiting,id_waiting


@pytest.mark.usefixtures("setup")
class TestSanity:

    def test_api(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders api's, on the way we nees to change the order status
        for the next test, so we use with all simulators, like payment for example
        because we need to raise the order status to 4 (payment status), then we change it to 5 (shipped)\n
        Date: 12/3/23\n
        """
        try:
            # creating new order
            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            # get the OrderStatusId how just created
            lastID = DbQueries().last_id()

            #  get all orders
            all_orders = self.api.get_orders()
            assert all_orders.status_code == 200
            self.log.send(self.config["TEST_PASS"].format("test_api", "get_orders", all_orders))

            #  get order by id
            res = self.api.get_order_by_id(lastID)
            assert res.status_code == 200
            self.log.send(self.config["TEST_PASS"].format("test_api", "get_order_by_id", res))

            # get card types from server
            res = self.api.get_cardtypes()
            assert res.status_code == 200
            self.log.send(self.config["TEST_PASS"].format("test_api", "get_cardtypes", res))

            # move the item to "cancel order" => id = 6"
            #  we can only do it with OrderStatusId is between 1-3
            res = self.api.cancel_order(lastID - 1)
            assert res.status_code == 200
            self.log.send(self.config["TEST_PASS"].format("test_api", "cancel_order", res))

            # move the item to "item in stock => id = 3"
            self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", lastID)
            # move the item to "payment succeeded" => id = 4"
            self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", lastID)

            #  move the item to "shipped" => id = 5"
            res = self.api.ship_order(lastID)
            assert res.status_code == 200
            self.log.send(self.config["TEST_PASS"].format("test_api", "ship_order", res))



        except AssertionError as ae:
            self.log.send(self.config["ASSERT_FAIL"].format("test_api", "UserCheckoutAcceptedIntegrationEvent", ae))
        except Exception as e:
            self.log.send(self.config["TEST_FAIL"].format("test_api", "UserCheckoutAcceptedIntegrationEvent", e))

    def test_successful_flow_mms(self):
        """
        Name: menahem rotblat\n
        Description: tests Orders flow (successfully)\n
        Date: 12/3/23\n
        """
        try:

            # creating new order

            self.basket.send_to_queue("UserCheckoutAcceptedIntegrationEvent")
            time.sleep(1)
            self.basket.consume()
            lastID = id_waiting()

            # print(msg_method)
            # wait for 20s (unless there is positive results) for status change on db
            # if return True so that status changed to 2: assertion will be True, otherwise False
            assert status_waiting(2)
            self.log.send(self.config["TEST_PASS"].format("test_successful_flow_mms", "UserCheckoutAcceptedIntegrationEvent", 2))

            # get the OrderStatusId how just created
            #  get all orders


            # self.log.send(self.config["TEST_PASS"].format("test_api", "get_orders", all_orders))

            #  get order by id


            # get card types from server

            # self.log.send(self.config["TEST_PASS"].format("test_api", "get_cardtypes", res))

            # move the item to "cancel order" => id = 6"
            #  we can only do it with OrderStatusId is between 1-3

            # self.log.send(self.config["TEST_PASS"].format("test_api", "cancel_order", res))

            # move the item to "item in stock => id = 3"
            # self.catalog.send_to_queue("OrderStockConfirmedIntegrationEvent", lastID)
            # move the item to "payment succeeded" => id = 4"
            # self.payment.send_to_queue("OrderPaymentSucceededIntegrationEvent", lastID)

            #  move the item to "shipped" => id = 5"
            # res = self.api.ship_order(lastID)

            # self.log.send(self.config["TEST_PASS"].format("test_api", "ship_order", res))

        except AssertionError as ae:
            self.log.send(self.config["ASSERT_FAIL"].format("test_api", "UserCheckoutAcceptedIntegrationEvent", ae))
        except Exception as e:
            self.log.send(self.config["TEST_FAIL"].format("test_api", "UserCheckoutAcceptedIntegrationEvent", e))

