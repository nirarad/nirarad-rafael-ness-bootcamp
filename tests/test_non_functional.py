from tests.functions_test import *

@pytest.mark.non_functional
@pytest.mark.update_check_successfully_status_4_to_5
def test_update_check_successfully_status_4_to_5(start_connect):
    """
    Test number: 4
    The test updates the order from "Paid" status (4) to "Shipped" status (5) -
    expected result: status 200
    :param start_connect: An instance of the Order API
    """
    # test mss, test number: 1

    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the object number from the json file, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB.
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Confirmation of successful payment, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        payment_success_test_and_expected_after_step_3(id_order, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_change_status(id_order) == 200

@pytest.mark.non_functional
@pytest.mark.update_check_failed_status_2_to_5
def test_update_check_failed_status_2_to_5(start_connect):
    """
    Test number: 5
    The test updates the order from "Awaitingvalidation" status (2) to "Shipped" status (5) -
    expected result: status 400
    :param start_connect: An instance of the Order API
    :return:
    """
    with MSSQLConnector() as db:
        # Creating an order - the function receives: object number in json, DB instance
        create_order_test_and_expected_after_step_1(0, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_change_status(id_order) == 400

@pytest.mark.non_functional
@pytest.mark.update_check_failed_status_3_to_5
def test_update_check_failed_status_3_to_5(start_connect):
    """
    Test number: 6
    The test updates the order from "Stockconfirmed" status (3) to "Shipped" status (5) -
    expected result: status 400
    :param start_connect: An instance of the Order API
    :return:
    """

    with MSSQLConnector() as db:
        # Creating an order - the function receives: object number in json, DB instance
        create_order_test_and_expected_after_step_1(0, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        # Sending confirmation from the catalog - the function receives: order number, DB
        catalog_success_test_and_expected_after_step_2(id_order, db)
        assert start_connect.put_change_status(id_order) == 400


@pytest.mark.non_functional
@pytest.mark.update_check_failed_status_5_to_6
def test_update_check_failed_status_5_to_6(start_connect):
    """
    Test number: 7
    The test updates the order from "Shipped" status (5) to "Cancelled" status (6) -
    expected result: status 400
    :param start_connect: An instance of the Order API
    :return:
    """
    # Runs test: 4
    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the object number from the json file, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB.
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Confirmation of successful payment, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        payment_success_test_and_expected_after_step_3(id_order, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_change_status(id_order) == 200
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_change_status(id_order) == 400

@pytest.mark.non_functional
@pytest.mark.cancel_order_successfully_status_1_to_6
def test_cancel_order_successfully_status_1_to_6(start_connect, start_docker):
    """
    Test number: 8
    The test cancels the order from "Submitted" status (1) to "Cancelled" status (6) -
    expected result: status 200
    :param start_connect: An instance of the Order API
    :param start_docker: An instance of the docker
    ----bug----
    """
    try:
        # Stop ordering.backgroundtasks in Docker
        start_docker.stop('eshop/ordering.backgroundtasks:linux-latest')
        with MSSQLConnector() as db:
            simulatorBasket = Basket()
            # create order with object number in json 0
            simulatorBasket.create_order(0)
            # The function waits until the status becomes 1
            re = simulatorBasket.waiting_for_an_update(1, db)
            assert re == 1
            # A query that returns the order that was last added
            id_order = get_last_added_to_db(db)
            assert start_connect.put_cancel_order(id_order) == 200
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(10)
    except Exception as e:
        start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
        l.writeLog(e)
        raise Exception(e)


@pytest.mark.non_functional
def test_cancel_order_successfully_status_2_to_6(start_connect):
    """
    Test number: 9
    The test cancels the order from "Awaitingvalidation" status (2) to "Cancelled" status (6) -
    expected result: status 200
    :param start_connect: An instance of the Order API
    :return:
    ----bug----
    """
    try:
        with MSSQLConnector() as db:
            # Creating an order - the function receives: object number in json, DB instance
            create_order_test_and_expected_after_step_1(0, db)
            # A query that returns the order that was last added
            id_order = get_last_added_to_db(db)
            assert start_connect.put_cancel_order(id_order) == 200
    except Exception as e:
        l.writeLog(e)
        raise Exception(e)

@pytest.mark.non_functional
@pytest.mark.cancel_order_successfully_status_3_to_6
def test_cancel_order_successfully_status_3_to_6(start_connect):
    """
    Test number: 10
    The test cancels the order from the status "Stockconfirmed" (3) to the status "Cancelled" (6) -
    expected result: status 200
    :param start_connect: An instance of the Order
    ---bug---
    """
    try:
        with MSSQLConnector() as db:
            # Creating an order - the function receives: object number in json, DB instance
            create_order_test_and_expected_after_step_1(0, db)
            # A query that returns the order that was last added
            id_order = get_last_added_to_db(db)
            # Sending confirmation from the catalog - the function receives: order number, DB
            catalog_success_test_and_expected_after_step_2(id_order, db)
            assert start_connect.put_cancel_order(id_order) == 200
    except Exception as e:
        l.writeLog(e)
        raise Exception(e)


def test_order_cancel_failure_4_to_6(start_connect):
    """
    Test number: 11
    The test cancels the order from "Paid" status (4) to "Cancelled" status (6) -
    expected result: status 400
    :param start_connect: An instance of the Order API
    :return:
    """
    with MSSQLConnector() as db:
        # test mss
        # step 1 -- create order and expected Result
        # The function receives - the object number from the json file, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB.
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Confirmation of successful payment, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        payment_success_test_and_expected_after_step_3(id_order, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_cancel_order(id_order) == 400

@pytest.mark.non_functional
@pytest.mark.order_cancel_failure_5_to_6
def test_order_cancel_failure_5_to_6(start_connect):
    """
    Test number: 12
    The test cancels the order from the status "shipped" (5) to the status "Cancelled" (6) -
    expected result: status 400
    :param start_connect: An instance of the Order API
    :return:
    """
    # Runs the test - test_update_check_successfully_status_4_to_5
    with MSSQLConnector() as db:
        # step 1 -- create order and expected Result
        # The function receives - the object number from the json file, db.
        create_order_test_and_expected_after_step_1(0, db)
        # Receiving the last order added to the DB
        id_order = get_last_added_to_db(db)
        # step 2 -- Confirmation from the catalog, that the product is in stock, and expected Result
        # The function receives - the ID of the order, DB.
        catalog_success_test_and_expected_after_step_2(id_order, db)
        # step 3 -- Confirmation of successful payment, and expected Result
        # The function receives - the ID of the order, DB, and an instance of API
        payment_success_test_and_expected_after_step_3(id_order, db)
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_change_status(id_order) == 200
        # A query that returns the order that was last added
        id_order = get_last_added_to_db(db)
        assert start_connect.put_cancel_order(id_order) == 400



@pytest.mark.non_functional
def test_get_order_with_an_incorrect_order_number(start_connect):
    assert start_connect.get_order_by_id(200000000)['status'] == 404