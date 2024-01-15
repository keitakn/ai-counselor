from typing import Literal
import tiktoken


def calculate_token_count(text: str, model: Literal["gpt-4", "gpt-3.5-turbo"]) -> int:
    tiktoken_encoding = tiktoken.encoding_for_model(model)
    encoded = tiktoken_encoding.encode(text)
    return len(encoded)


DEFAULT_MAX_TOKEN_LIMIT = 1000


def is_token_limit_exceeded(
    use_token: int, max_token_limit: int = DEFAULT_MAX_TOKEN_LIMIT
) -> bool:
    return use_token > max_token_limit
