from typing import TypedDict
from usecase.db_handler_interface import DbHandlerInterface
from domain.repository.generate_message_repository_interface import (
    GenerateMessageRepositoryDto,
    GenerateMessageRepositoryInterface,
)
from domain.repository.conversation_history_repository_interface import (
    ConversationHistoryRepositoryInterface,
    SaveConversationHistoryDto,
)
from log.logger import AppLogger, SuccessLogExtra, ErrorLogExtra


class GenerateMessageUseCaseDto(TypedDict):
    request_id: str
    user_id: str
    message: str
    db_handler: DbHandlerInterface
    generate_message_repository: GenerateMessageRepositoryInterface
    conversation_history_repository: ConversationHistoryRepositoryInterface


class GenerateMessageUseCaseResult(TypedDict):
    message: str


class GenerateMessageUseCase:
    def __init__(self, dto: GenerateMessageUseCaseDto) -> None:
        app_logger = AppLogger()
        self.logger = app_logger.logger
        self.dto = dto

    async def execute(
        self,
    ) -> GenerateMessageUseCaseResult:
        user_id: str = self.dto["user_id"]

        generate_message_repository_dto = GenerateMessageRepositoryDto(
            user_id=user_id,
            message=self.dto["message"],
        )

        try:
            generate_message_result = await self.dto[
                "generate_message_repository"
            ].generate_message(generate_message_repository_dto)

            await self.dto["db_handler"].begin()

            save_conversation_history_dto = SaveConversationHistoryDto(
                user_id=user_id,
                user_message=self.dto["message"],
                ai_message=generate_message_result.get("message"),
            )
            await self.dto["conversation_history_repository"].save_conversation_history(
                save_conversation_history_dto,
            )

            await self.dto["db_handler"].commit()

            self.logger.info(
                "success",
                extra=SuccessLogExtra(
                    request_id=self.dto["request_id"],
                    user_id=user_id,
                    ai_response_id=generate_message_result.get("ai_response_id"),
                ),
            )

            return GenerateMessageUseCaseResult(
                message=generate_message_result.get("message"),
            )
        except Exception as e:
            await self.dto["db_handler"].rollback()

            self.logger.error(
                f"An error occurred while creating the message: {str(e)}",
                exc_info=True,
                extra=ErrorLogExtra(
                    request_id=self.dto["request_id"],
                    user_id=self.dto["user_id"],
                ),
            )

            raise e
        finally:
            self.dto["db_handler"].close()
