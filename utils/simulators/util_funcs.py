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
    while span < 20:
        if DbQueries().check_OrderStatusId(DbQueries().last_id()) == status:
            return True
        time.sleep(1)
        span += 1
    return False
