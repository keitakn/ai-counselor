from typing import TypedDict
from domain.repository.generate_message_repository_interface import (
    GenerateMessageRepositoryDto,
    GenerateMessageRepositoryInterface,
)
from log.logger import AppLogger, SuccessLogExtra


class GenerateMessageUseCaseDtoRequiredType(TypedDict):
    request_id: str
    message: str
    generate_message_repository: GenerateMessageRepositoryInterface


class GenerateMessageUseCaseDtoOptionalType(TypedDict, total=False):
    conversation_id: str


class GenerateMessageUseCaseDto(
    GenerateMessageUseCaseDtoRequiredType,
    GenerateMessageUseCaseDtoOptionalType,
):
    pass


class GenerateMessageUseCaseResult(TypedDict):
    conversation_id: str
    message: str


class GenerateMessageUseCase:
    def __init__(self, dto: GenerateMessageUseCaseDto) -> None:
        app_logger = AppLogger()
        self.logger = app_logger.logger
        self.dto = dto

    async def execute(
        self,
    ) -> GenerateMessageUseCaseResult:
        conversation_id: str = self.dto["request_id"]

        generate_message_repository_dto = GenerateMessageRepositoryDto(
            conversation_id=conversation_id,
            message=self.dto["message"],
        )

        generate_message_result = await self.dto[
            "generate_message_repository"
        ].generate_message(generate_message_repository_dto)

        self.logger.info(
            "success",
            extra=SuccessLogExtra(
                request_id=self.dto["request_id"],
                conversation_id=conversation_id,
                ai_response_id=generate_message_result.get("ai_response_id"),
            ),
        )

        return GenerateMessageUseCaseResult(
            conversation_id=conversation_id,
            message=generate_message_result.get("message"),
        )
