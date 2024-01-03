from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, Field
from http import HTTPStatus
from domain.unique_id import is_uuid_format, generate_unique_id
from domain.message import is_message
from log.logger import AppLogger, ErrorLogExtra
from usecase.generate_message_use_case import (
    GenerateMessageUseCase,
    GenerateMessageUseCaseDto,
)
from infrastructure.repository.openai.openai_generate_message_repository import (
    OpenAiGenerateMessageRepository,
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
            repository = OpenAiGenerateMessageRepository()

            use_case = GenerateMessageUseCase(
                GenerateMessageUseCaseDto(
                    request_id=unique_id,
                    message=self.request_body.message,
                    generate_message_repository=repository,
                )
            )

            use_case_result = await use_case.execute()

            return JSONResponse(
                status_code=HTTPStatus.OK,
                headers=response_headers,
                content=use_case_result,
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
                content=unexpected_error,
            )
