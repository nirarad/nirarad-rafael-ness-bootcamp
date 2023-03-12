import time

from utils.db.db_queries import DbQueries


def waiting_and_return_bool(status) -> bool:
    global span
    span = 0
    while span < 20:
        if DbQueries().check_OrderStatusId(DbQueries().last_id()) == status:
            return True
        time.sleep(1)
        span += 1
    return False
