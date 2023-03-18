
import sys
sys.path.insert(1, r'C:\Users\Hana Danis\Downloads\Bootcamp-automation\esh\eShopOnContainersPro\rafael-ness-bootcamp')
import time
from dotenv import load_dotenv
from utils.db.db_utils import MSSQLConnector
import os


load_dotenv()


class Queries:

    @staticmethod
    def _run_query(query, *args):
        with MSSQLConnector() as conn:
            return conn.select_query(query.format(*args))

    def get_last_ordering(self):
        return self._run_query(os.getenv('LAST_ORDER'))[0]['Id']

    def count_order(self):
        return self._run_query(os.getenv('COUNT_ORDER'))[0]['']
    
    def get_status(self, status1, status2, sec=60):
        order_id = self.get_last_ordering()
        query = os.getenv('ORDER_STATUS')
        start_time = time.time()
        while status1!= status2 and time.time() - start_time < sec:
            order_id = self.get_last_ordering()
            status1 = self._run_query(f'{query} = {order_id}')[0]['OrderStatusId']
        return status1   