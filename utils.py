def is_int(value):
    try:
        s = int(value)
        return True
    except Exception:
        return False
