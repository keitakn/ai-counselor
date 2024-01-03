import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, Field
from http import HTTPStatus
from domain.unique_id import is_uuid_format, generate_unique_id
from domain.message import is_message
from log.logger import AppLogger, ErrorLogExtra
from openai import AsyncOpenAI


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


class GenerateMessageErrorResponseBody(BaseModel):
    type: str
    title: str


class GenerateMessageController:
    def __init__(self, request_body: GenerateMessageRequestBody) -> None:
        app_logger = AppLogger()
        self.logger = app_logger.logger
        self.request_body = request_body

    async def exec(self) -> JSONResponse:
        unique_id = generate_unique_id()

        conversation_id = unique_id
        if self.request_body.conversation_id is not None and is_uuid_format(
            self.request_body.conversation_id
        ):
            conversation_id = self.request_body.conversation_id

        response_headers = {"Ai-Counselor-Request-Id": unique_id}

        try:
            client = AsyncOpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
            )

            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": self.request_body.message,
                    }
                ],
                model="gpt-3.5-turbo",
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                headers=response_headers,
                content={
                    "conversation_id": conversation_id,
                    "message": chat_completion.choices[0].message.content,
                },
            )
        except Exception as e:
            unexpected_error = GenerateMessageErrorResponseBody(
                type="INTERNAL_SERVER_ERROR",
                title="an unexpected error has occurred.",
            )

            extra = ErrorLogExtra(
                request_id=unique_id,
                conversation_id=conversation_id,
            )

            self.logger.error(
                str(e),
                exc_info=True,
                extra=extra,
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                headers=response_headers,
                content=unexpected_error.model_dump(),
            )
