def to_bool(val):
    if isinstance(val, bool):
        return val
    elif isinstance(val, str):
        isFalse = val.lower().strip() in ["false", "0", "no", "n", "off"]
        return not isFalse
    return bool(val)