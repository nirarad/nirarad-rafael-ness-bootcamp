import pytest

from utils.db.db_utils import MSSQLConnector


@pytest.mark.usefixtures("setup")
class DbQueries:
    def last_id(self):
        with MSSQLConnector() as db:
            r = db.select_query("SELECT top 1 * from ordering.orders ORDER BY Id DESC")
            return r[0]["Id"]

    def check_OrderStatusId(self, order_id):
        with MSSQLConnector() as db:
            res = db.select_query(f"SELECT * from ordering.orders where Id = {order_id}")
            return res[0]["OrderStatusId"]