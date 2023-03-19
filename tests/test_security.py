from tests.functions import *

@pytest.mark.security
def test_user_request_with_invalid_token(start_connect):
    """
    Test number: 22
    Test with invalid token,
    expected result: 401 status
    :param start_connect:
    security
    # pass
    """
    assert start_connect.get_order_by_id(1, authorization=False).status_code == 401

@pytest.mark.security
@pytest.mark.ecurity_connect_user_for_user_another_get
def test_security_connect_user_for_user_another_get(start_connect):
    """
    Test number:19
    ----bug----
    security
    """
    try:
        api_bob = OrderingAPI("bob", "Pass123%24")
        with MSSQLConnector() as db:
            id_order = db.select_query(
                'select TOP (1) id from [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] where BuyerId = 2')

            api_bob.get_order_by_id(id_order[0]['id'])
            id_order = db.select_query(
                'select TOP (1) id from [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] where BuyerId = 1')
            assert api_bob.get_order_by_id(id_order[0]['id']) == 401
    except Exception as e:
        l.writeLog(e)
        raise Exception(f'this bag {e}')


@pytest.mark.security
def test_security_connect_user_for_user_another_cancel():
    """
    Test number: 20
    The function connects with Bob and tries to cancel another user's order
    :return:
    security
    """
    api_bob = OrderingAPI("bob", "Pass123%24")
    with MSSQLConnector() as db:
        id_order = db.select_query(
            'select TOP (1) id from [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] where BuyerId = 1 and [OrderStatusId] = 3')
        assert api_bob.put_cancel_order(id_order[0]['id']) == 400

@pytest.mark.security
def test_security_connect_user_for_user_another_update():
    """
    Test number: 21
    The function connects with one user and tries to update another user's order
    :return:
    security
    """
    api_bob = OrderingAPI("bob", "Pass123%24")
    with MSSQLConnector() as db:
        id_order = db.select_query(
            'select TOP (1) id from [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] where '
            'BuyerId = 1 and [OrderStatusId] = 3')
        assert api_bob.put_change_status(id_order[0]['id']) == 400

