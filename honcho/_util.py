import collections

def _get_if_empty(a, b):
    return a if a else b

def _listify(a):
    if isinstance(a, (list, tuple)):
        return a
    return [a]