import time

from utils.db.db_queries import DbQueries


def id_waiting() -> int:
    span = 0
    while span <= 5:
        time.sleep(1)
        span += 1
    return DbQueries().last_id()


def status_waiting(status) -> bool:
    span = 0
    order_id = DbQueries().last_id()
    while span < 50:
        if DbQueries().check_OrderStatusId(order_id) == status:
            return True
        time.sleep(1)
        span += 1
    return False

