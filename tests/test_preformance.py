from tests.functions_test import *


@pytest.mark.preformance
def test_reliability_create_order_before_status_1(start_docker):
    """
    :param start_docker:
    :return:
    """
    try:
        with MSSQLConnector() as db:
            # Saving the number of orders
            count_before = get_count_order(db)
            start_docker.stop('eshop/ordering.backgroundtasks:linux-latest')
            simulatorBasket = Basket()
            simulatorBasket.create_order(0)
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(5)
            count_after = get_count_order(db)
            assert count_before + 1 == count_after
    except Exception as e:
        start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
        l.writeLog(f"Filed in - test_reliability_create_order ,{e}")
        raise Exception(f"Filed in - test_reliability_create_order {e}")
@pytest.mark.preformance
def test_reliability_create_order_after_status_1(start_docker):
    """
    :param start_docker:
    :return:
    """
    try:
        with MSSQLConnector() as db:
            # Saving the number of orders
            start_docker.stop('eshop/ordering.backgroundtasks:linux-latest')
            simulatorBasket = Basket()
            simulatorBasket.create_order(0)
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(10)
            re = simulatorBasket.waiting_for_an_update(2, db)
            assert re == 2

    except Exception as e:
        start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
        l.writeLog(f"Filed in - test_reliability_create_order ,{e}")
        raise Exception(f"Filed in - test_reliability_create_order {e}")

@pytest.mark.preformance
@pytest.mark.reliability
def test_reliability_ordering_backgroundtasks_after_status_2(start_docker):
    """
    Test number: 14
    chana kadosh
    The test checks the reliability of the server,(after status 2)
    downloading the API order server in the middle of placing an order,
    and then raising the server and continuing the operation, trying to ensure reliability
    :return:
    """
    with MSSQLConnector() as db:
        try:
            # Creating an order - the function receives: object number in json, DB instance
            create_order_test_and_expected_after_step_1(0, db)
            # A query that returns the order that was last added
            id_order = get_last_added_to_db(db)
            # Stops the ordering.api server
            start_docker.stop('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(10)
            # start the ordering.api server
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(20)
            simulatorCatalog = Catalog()
            simulatorCatalog.catalog_in_stock(id_order)
            re = simulatorCatalog.waiting_for_an_update(3, db)
            assert re == 3
        except Exception as e:
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            l.writeLog(f"Failed in - test_reliability_ordering_backgroundtasks function, parameter id: {id_order}, {e}")
            raise Exception(f"Filed in - test_reliability_ordering_backgroundtasks {e}")

@pytest.mark.preformance
@pytest.mark.reliability
def test_reliability_ordering_backgroundtasks_after_status_3(start_docker):
    """
    Test number:
    chana kadosh
    The test checks the reliability of the server,(after status 3)
    downloading the API order server in the middle of placing an order,
    and then raising the server and continuing the operation, trying to ensure reliability
    :return:
    """
    with MSSQLConnector() as db:
        try:
            # Creating an order - the function receives: object number in json, DB instance
            create_order_test_and_expected_after_step_1(0, db)
            # A query that returns the order that was last added
            id_order = get_last_added_to_db(db)
            catalog_success_test_and_expected_after_step_2(id_order, db)
            # Stops the ordering.api server
            start_docker.stop('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(20)
            # start the ordering.api server
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            time.sleep(20)
            simulatorPayment = Payment()
            simulatorPayment.payment_success(id_order)
            # Waiting until the status becomes 4
            re = simulatorPayment.waiting_for_an_update(4, db)
            assert re == 4
        except Exception as e:
            start_docker.start('eshop/ordering.backgroundtasks:linux-latest')
            l.writeLog(f"Failed in - test_reliability_ordering_backgroundtasks function, parameter id: {id_order}, {e}")
            raise Exception(f"Filed in - test_reliability_ordering_backgroundtasks {e}")



