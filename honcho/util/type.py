def sequencify(value, type_=list):
    if not isinstance(value, (list, tuple)):
        value = [value]

    value = type_(value)

    return value
