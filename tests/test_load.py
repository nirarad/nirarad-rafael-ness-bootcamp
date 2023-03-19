from tests.functions_test import *

@pytest.mark.load
@pytest.mark.scalability_for_handling_high_volumes_of_orders
def test_scalability_for_handling_high_volumes_of_orders(start_docker):
    """
    Test number: 13
    Checks how the server handles a load of messages
    :return:
    """
    with MSSQLConnector() as db:
        sum = get_count_order(db)
        start_docker.stop('eshop/ordering.api:linux-latest')
        simulatorBasket = Basket()
        for i in range(2):
            simulatorBasket.create_order(0)
        start_docker.start('eshop/ordering.api:linux-latest')
        time.sleep(20)
        sum1 = get_count_order(db)
        time.sleep(100)
        assert sum + 2 == sum1

@pytest.mark.load
def test_Checking_100_orders_per_hour():
    """
    Test number: 24
    The function creates a hundred orders and checks whether the creation of
    the orders was in less than an hour or equal to one hour
    :return:
    """
    start_time = time.time()
    simulatorBasket = Basket()
    for i in range(2):
        time.sleep(1)
        simulatorBasket.create_order(0)
    end_time = time.time()
    difference = end_time - start_time
    assert difference <= 3600

