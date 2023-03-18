# Instructions:
# Download https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
import pprint

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

    def orderStatusid(self, id):
        with MSSQLConnector() as conn:
            return conn.select_query(f'SELECT orderStatusid from ordering.orders where id={id}')[0]['orderStatusid']

    def select_last_id(self):
        with MSSQLConnector() as conn:
            return conn.select_query('SELECT max(id) from ordering.orders')[0]['']

    def available_stock(self):
        with MSSQLConnector() as conn:
            return conn.select_query('SELECT AvailableStock from [Microsoft.eShopOnContainers.Services.CatalogDb].[dbo].[Catalog]')[0]['AvailableStock']


# class DbUtils:
#
#     @staticmethod
#     def statuscode_byID(id):
#         """
#
#         :param id:
#         :return:
#         """
#         x = 0
#         with MSSQLConnector() as conn:
#             x = (conn.select_query(f'SELECT * from ordering.orders WHERE Id = {id}'))
#
#         return x[0]['OrderStatusId']

if __name__ == '__main__':
    # print(MSSQLConnector().orderStatusid(1))
    # print(MSSQLConnector().select_last_id())
    print(MSSQLConnector().available_stock())

