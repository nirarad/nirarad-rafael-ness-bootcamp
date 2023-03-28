from utils.db.db_utils import MSSQLConnector
import os
from dotenv import load_dotenv

load_dotenv()


def last_order_id():
    with MSSQLConnector() as sql:
        result = sql.select_query(os.getenv('ID_QUERY'))
    return result[0]['Id']


def last_order_status():
    with MSSQLConnector() as sql:
        result = sql.select_query(os.getenv('STATUS_QUERY'))
    return result[0]['OrderStatusId']


if __name__ == '__main__':
    last_order_status()
