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
from domain.unique_id import is_uuid_format

router = APIRouter()


class GenerateMessageJsonResponse(BaseModel):
    conversation_id: str = Field(
        default=None,
        description="会話の一意なID。UUID形式である必要があります。",
        json_schema_extra={
            "examples": ["f4f4d2ee-770f-4b6d-90c9-16cf918ae3be"],
        },
    )
    message: str = Field(
        ...,
        description="送信するメッセージの内容。",
        json_schema_extra={
            "examples": ["こんにちは、悩みを聞いてください。"],
        },
    )

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(cls, v: str) -> str:
        if not is_uuid_format(v):
            raise ValueError(f"'{v}' is not in UUID format")
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

    - **conversationId**: 会話の一意なID。
    - **message**: エンドユーザーから送信されるメッセージの内容。
    """

    controller = GenerateMessageController(request, request_body)

    return await controller.exec()
