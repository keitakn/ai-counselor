from fastapi import APIRouter
from pydantic import BaseModel, field_validator, Field
from http import HTTPStatus
from starlette.responses import JSONResponse
from openai import AsyncOpenAI
import os
from domain.message import is_message
from domain.unique_id import is_uuid_format
from starlette.requests import Request

router = APIRouter()

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


class GenerateMessageRequestBody(BaseModel):
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
            "examples": ["こんにちは"],
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
    request: Request, request_body: GenerateMessageRequestBody
) -> JSONResponse:
    """
    このエンドポイントはAIが生成したメッセージを返します。

    - **conversationId**: 会話の一意なID。
    - **message**: エンドユーザーから送信されるメッセージの内容。
    """

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": request_body.message,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={
            "conversation_id": request_body.conversation_id,
            "message": chat_completion.choices[0].message.content,
        },
    )
