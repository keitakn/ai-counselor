import re


def is_user_id(value: str) -> bool:
    pattern = r"^[a-zA-Z0-9-_]{1,36}$"

    return bool(re.match(pattern, value))
