# Instructions:
# Download https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
import json
import time

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

    def req_query(self, req):
        with MSSQLConnector() as conn:
            # pprint.pprint(conn.select_query(req))
            return conn.select_query(req)

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


if __name__ == '__main__':
    import pprint

    # with MSSQLConnector() as conn:
    #     pprint.pprint(conn.select_query('SELECT * from ordering.orders'))

    # MSSQLConnector().req_query('SELECT * from ordering.orders')
    # a = MSSQLConnector().req_query('SELECT Id,OrderStatusId from ordering.orders ORDER BY Id DESC')[0]
    # print(a)


    a = MSSQLConnector().req_query('SELECT top 1 Id from ordering.orders ORDER BY Id DESC')[0]['Id']
    b = MSSQLConnector().req_query(f'SELECT count(Id) as amount, OrderStatusId from ordering.orders where Id > ({a}) GROUP BY OrderStatusId')
    c = MSSQLConnector().req_query(f'SELECT amount from (SELECT count(Id) as amount, OrderStatusId from ordering.orders where Id >= ({a}) GROUP BY OrderStatusId) o where OrderStatusId = 4')[0]['amount']
    print(c)

