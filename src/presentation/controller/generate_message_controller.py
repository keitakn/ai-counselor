from fastapi.responses import JSONResponse
from starlette.requests import Request
from pydantic import BaseModel, field_validator, Field
from http import HTTPStatus
from domain.user_id import is_user_id
from domain.message import is_message
from log.logger import AppLogger, ErrorLogExtra
from usecase.generate_message_use_case import (
    GenerateMessageUseCase,
    GenerateMessageUseCaseDto,
)
from presentation.request_id import extract_and_validate_request_id
from infrastructure.db import create_db_connection
from infrastructure.repository.aiomysql.aiomysql_db_handler import AiomysqlDbHandler
from infrastructure.repository.aiomysql.aiomysql_conversation_history_repository import (
    AiomysqlConversationHistoryRepository,
)
from infrastructure.repository.openai.openai_generate_message_repository import (
    OpenAiGenerateMessageRepository,
)


class GenerateMessageRequestBody(BaseModel):
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
            "examples": ["こんにちは"],
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


class GenerateMessageErrorResponseBody(BaseModel):
    type: str
    title: str


class GenerateMessageController:
    def __init__(
        self, request: Request, request_body: GenerateMessageRequestBody
    ) -> None:
        app_logger = AppLogger()
        self.logger = app_logger.logger
        self.request = request
        self.request_body = request_body

    async def exec(self) -> JSONResponse:
        request_id_or_error = extract_and_validate_request_id(self.request)
        if isinstance(request_id_or_error, JSONResponse):
            return request_id_or_error

        request_id = request_id_or_error

        response_headers = {"Ai-Counselor-Request-Id": request_id}

        try:
            connection = await create_db_connection()

            db_handler = AiomysqlDbHandler(connection)

            generate_message_repository = OpenAiGenerateMessageRepository()

            conversation_history_repository = AiomysqlConversationHistoryRepository(
                connection
            )

            use_case = GenerateMessageUseCase(
                GenerateMessageUseCaseDto(
                    request_id=request_id,
                    user_id=self.request_body.user_id,
                    message=self.request_body.message,
                    db_handler=db_handler,
                    generate_message_repository=generate_message_repository,
                    conversation_history_repository=conversation_history_repository,
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
                request_id=request_id,
                user_id=self.request_body.user_id,
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
