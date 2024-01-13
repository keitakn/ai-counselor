import pytest
from domain.user_id import is_user_id

test_cases = [
    ("0cdeb54d-0f11-4800-8a45-47f2886db845", True),
    ("user_123-456", True),
    ("a" * 36, True),
    ("user@invalid", False),
    ("a" * 37, False),
    ("", False),
    ("user$%^&", False),
    (" ", False),
    ("a" * 37, False),
]


@pytest.mark.parametrize("user_id, expected", test_cases)
def test_is_user_id(user_id, expected):
    assert is_user_id(user_id) == expected
