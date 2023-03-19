from datetime import datetime


def get_current_time():
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    return time
