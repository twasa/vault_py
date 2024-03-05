from datetime import datetime


def unix_time_now_int():
    return int(datetime.utcnow().timestamp())


def unix_time_now_float():
    return datetime.utcnow().timestamp()
