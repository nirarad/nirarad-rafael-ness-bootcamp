import json
import time

import dotenv

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


def change_ddt(file, key, value) -> dict:
    """
    Name: Menahem Rotblat.\n
    Description: takes data and return a copy with changes.\n
    Date: 16/03/23
    :param file: string, to make change
    :param key: string, name of param to change
    :param value: string, the change
    :return: dict
    """
    config = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../../.env"))
    data = json.load(open(config[file]))
    data[key] = value
    return data
