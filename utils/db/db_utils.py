import pyodbc
import os
from dotenv import load_dotenv


class MSSQLConnector:

    def __init__(self):
        load_dotenv('D:/eShopProject/rafael-ness-bootcamp/tests/DATA/.env.test')
        self.SERVER = str(os.getenv('SERVER'))
        self.USER = os.getenv('USER')
        self.PASSWORD = os.getenv('PASSWORD')
        self.DATABASE = os.getenv('DATABASE')
        self.DRIVER = os.getenv('DRIVER')
        self.connection_str = f"Driver={self.DRIVER};Server={self.SERVER};" \
                              f"Database={self.DATABASE};UID={self.USER};PWD={self.PASSWORD};TrustServerCertificate=yes"
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

    def update_order_db_status(self, db_order_id, to_id):
        query = 'Update [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] ' \
                f'set OrderStatusId = {to_id}' \
                f'where Id = {db_order_id}'
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.commit()
        return True

    def get_order_status_from_db(self, order_id):
        query = 'select o.OrderStatusId from [Microsoft.eShopOnContainers.Services.OrderingDb].ordering.orders as o ' \
                f'where Id = {order_id}'
        cursor = self.conn.cursor()
        cursor.execute(query)
        order_status = cursor.fetchall()
        return order_status[0][0]

    def get_last_order_record_id_in_db(self):
        query = 'select TOP 1 o.Id from [Microsoft.eShopOnContainers.Services.OrderingDb].ordering.orders as o order ' \
                'by Id desc'
        cursor = self.conn.cursor()
        cursor.execute(query)
        last_order_id = cursor.fetchall()
        if len(last_order_id) > 0:
            return last_order_id[0][0]
        else:
            return -1

    def delete_order_in_db(self,db_order_id):
        query = f'delete FROM [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders]' \
                f' where Id = {db_order_id}'
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.commit()
        return True

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    from pprint import pprint as p

    with MSSQLConnector() as conn:
        query = 'Update [Microsoft.eShopOnContainers.Services.OrderingDb].[ordering].[orders] ' \
                'set OrderStatusId = 4' \
                'where Id = 161'
        # pprint.pprint(conn.select_query('SELECT * from ordering.orders'))
        # p(conn.get_order_status_from_db(151))
        # conn.update_order_db_id(161, 1)
        # p(conn.get_order_status_from_db(151))
        p(conn.get_last_order_record_id_in_db())
