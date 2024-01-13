import aiomysql
from domain.repository.conversation_history_repository_interface import (
    SaveConversationHistoryDto,
    ConversationHistoryRepositoryInterface,
)


class AiomysqlConversationHistoryRepository(ConversationHistoryRepositoryInterface):
    def __init__(self, connection: aiomysql.Connection) -> None:
        self.connection = connection

    async def save_conversation_history(self, dto: SaveConversationHistoryDto) -> None:
        async with self.connection.cursor() as cursor:
            sql = """
            INSERT INTO conversation_histories
            (user_id, user_message, ai_message)
            VALUES (%s, %s, %s)
            """
            await cursor.execute(
                sql,
                (
                    dto["user_id"],
                    dto["user_message"],
                    dto["ai_message"],
                ),
            )
