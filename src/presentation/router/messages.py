from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel, field_validator, Field
from starlette.responses import JSONResponse
from starlette.requests import Request
from presentation.auth import basic_auth
from presentation.controller.generate_message_controller import (
    GenerateMessageController,
    GenerateMessageRequestBody,
)
from domain.message import is_message
from domain.user_id import is_user_id

router = APIRouter()


class GenerateMessageJsonResponse(BaseModel):
    user_id: str = Field(
        default=None,
        description="ユーザーID。半角英数字と-_のみ利用可能です。",
        json_schema_extra={
            "examples": ["Ua000xxxxxxxxxxxxxxxxxxxxxxxxxxxx"],
        },
    )
    message: str = Field(
        ...,
        description="送信するメッセージの内容。",
        json_schema_extra={
            "examples": ["こんにちは、悩みを聞いてください。"],
        },
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        if not is_user_id(v):
            raise ValueError(f"'{v}' is not in user_id format")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not is_message(v):
            raise ValueError(
                "message must be at least 2 character and no more than 5,000 characters"
            )
        return v


@router.post("/v1/messages", response_model=GenerateMessageJsonResponse)
async def generate_message(
    request: Request,
    request_body: GenerateMessageRequestBody,
    credentials: HTTPBasicCredentials = Depends(basic_auth),
) -> JSONResponse:
    """
    このエンドポイントはAIが生成したメッセージを返します。

    - **userId**: ユーザーの識別子。
    - **message**: エンドユーザーから送信されるメッセージの内容。
    """

    controller = GenerateMessageController(request, request_body)

    return await controller.exec()
