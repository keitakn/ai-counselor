import re
from typing import Union, Optional, Any
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import StreamingResponse, JSONResponse


MAX_REQUEST_ID_LENGTH = 255
ALLOWED_CHARACTERS_PATTERN = r"^[a-zA-Z0-9_-]+$"


class ValidateRequestIdResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None


def validate_request_id(value: Any):
    if value is None:
        return ValidateRequestIdResponse(
            is_valid=False,
            error_message="Please include 'ai-counselor-request-id' in the request Header.",
        )

    if not isinstance(value, str) or len(value) == 0:
        return ValidateRequestIdResponse(
            is_valid=False,
            error_message="'ai-counselor-request-id' is required. A unique string is recommended if possible.",
        )

    if not re.match(ALLOWED_CHARACTERS_PATTERN, value):
        return ValidateRequestIdResponse(
            is_valid=False,
            error_message="'ai-counselor-request-id' contains invalid characters. Only alphabets, '_', and '-' are allowed.",  # noqa: E501
        )

    if len(value) <= MAX_REQUEST_ID_LENGTH:
        return ValidateRequestIdResponse(is_valid=True)

    return ValidateRequestIdResponse(
        is_valid=False,
        error_message=f"'ai-counselor-request-id' should not exceed {MAX_REQUEST_ID_LENGTH} characters.",
    )


def extract_and_validate_request_id(
    request: Request,
) -> Union[str, StreamingResponse, JSONResponse]:
    request_id = request.headers.get("ai-counselor-request-id", None)
    validate_result = validate_request_id(request_id)
    if validate_result.is_valid is False and validate_result.error_message:
        detail = validate_result.error_message

        bad_request_response_body = {
            "type": "BAD_REQUEST",
            "title": "invalid Request Header.",
            "detail": detail,
        }

        return JSONResponse(
            bad_request_response_body,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return request_id
