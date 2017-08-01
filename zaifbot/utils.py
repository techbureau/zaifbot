import time


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
