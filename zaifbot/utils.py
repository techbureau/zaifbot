def merge_dict(base_dict, *dicts):
    for dic in dicts:
        base_dict.update(dic) or base_dict
    return base_dict
