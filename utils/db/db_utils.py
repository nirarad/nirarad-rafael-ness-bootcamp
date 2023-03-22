# Instructions:
# Download https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
import pyodbc


class MSSQLConnector:
    def __init__(self, database='OrderingDb'):
        self.SERVER = '127.0.0.1,5433'
        self.USER = 'sa'
        self.PASSWORD = 'Pass@word'
        self.DATABASE = f'Microsoft.eShopOnContainers.Services.{database}'
        self.DRIVER = '{ODBC Driver 18 for SQL Server}'
        self.connection_str = f"Driver={self.DRIVER};Server={self.SERVER};Database={self.DATABASE};UID={self.USER};PWD={self.PASSWORD};TrustServerCertificate=yes"
        self.conn = None

    def __enter__(self):
        self.conn = pyodbc.connect(self.connection_str)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def select_query(self, query):
        """Executes a select query on the database and returns a list of dictionaries per row"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def close(self):
        self.conn.close()


class DbUtils:

    @staticmethod
    def statuscode_byID(id):
        """
        method gets status code by order id
        """
        x = 0
        with MSSQLConnector() as conn:
            return conn.select_query(f'SELECT OrderStatusId from ordering.orders WHERE Id = {id}')[0]['OrderStatusId']

    @staticmethod
    def get_max_orders_id():
        """
        method gets max order id (the last order)
        """
        with MSSQLConnector() as conn:
            return conn.select_query(f'SELECT max(id) from ordering.orders')[0]['']

    @staticmethod
    def get_orders_greater_than_id(idx):
        """
        method gets all the orders with order id greater than the given order id
        """
        with MSSQLConnector() as conn:
            return conn.select_query(f'SELECT * from ordering.orders where id > {idx}')

    @staticmethod
    def get_item_quantity(idy):
        """
        method gets the quantity by the item by its id
        """
        with MSSQLConnector() as conn:
            return (conn.select_query(
                f'SELECT AvailableStock from [Microsoft.eShopOnContainers.Services.CatalogDb].[dbo].[Catalog] where Id = {idy}'))[
                0]['AvailableStock']

    @staticmethod
    def get_orders_id(user_id):
        """
        method gets all orders id by user id (all the orders that belongs to this user)
        """
        with MSSQLConnector() as conn:
            return (conn.select_query(
                f'SELECT Id from ordering.orders where BuyerId = {user_id}'
            ))


if __name__ == '__main__':
    # import pprint
    # print(DbUtils.statuscode_byID(551))
    # print(DbUtils.get_orders_greater_than_id(2210))
    # with MSSQLConnector() as conn:
    # pprint.pprint(conn.select_query('SELECT * from ordering.orders'))
    # print(DbUtils.get_item_quantity(1))
    print(DbUtils.get_orders_id(11))
