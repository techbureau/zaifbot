import time
import random


# for dict
def merge_dict(base_dict, *dicts):
    for dic in dicts:
        base_dict.update(dic) or base_dict
    return base_dict


def datetime2timestamp(datetime):
    return int(time.mktime(datetime.timetuple()))


def int_epoch_time(t=None):
    if not t:
        return int(time.time())
    return int(t)


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def random_sleep(from_, to_):
    sleeping_time = random.uniform(from_, to_)
    time.sleep(sleeping_time)
