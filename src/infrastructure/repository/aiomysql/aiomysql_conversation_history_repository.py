from typing import cast, List, Literal
import aiomysql
from domain.message import ChatMessage
from domain.prompt import create_prompt
from domain.repository.conversation_history_repository_interface import (
    SaveConversationHistoryDto,
    CreateMessagesWithConversationHistoryDto,
    ConversationHistoryRepositoryInterface,
)
from infrastructure.openai import calculate_token_count, is_token_limit_exceeded


class AiomysqlConversationHistoryRepository(ConversationHistoryRepositoryInterface):
    def __init__(self, connection: aiomysql.Connection, max_token_limit: int) -> None:
        self.connection = connection
        self.max_token_limit = max_token_limit

    async def create_messages_with_conversation_history(
        self, dto: CreateMessagesWithConversationHistoryDto
    ) -> List[ChatMessage]:
        async with self.connection.cursor() as cursor:
            sql = """
            SELECT user_message, ai_message
            FROM conversation_histories
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 10
            """
            await cursor.execute(sql, (dto["user_id"],))
            result = await cursor.fetchall()
            if result:
                result.reverse()

            conversation_history = [
                {"role": role_type, "content": row[message_type]}
                for row in result
                for role_type, message_type in [
                    ("user", "user_message"),
                    ("assistant", "ai_message"),
                ]
            ]

        # もし会話履歴がまだ存在しなければ、システムメッセージを追加
        if not conversation_history:
            conversation_history.append({"role": "system", "content": create_prompt()})

        # 新しいメッセージを会話履歴に追加
        conversation_history.append({"role": "user", "content": dto["request_message"]})

        # 実際に会話履歴に含めるメッセージ
        chat_messages: List[ChatMessage] = []
        total_tokens = 0

        for message in reversed(conversation_history):
            message_tokens = calculate_token_count(message["content"], "gpt-4")
            if (
                is_token_limit_exceeded(
                    total_tokens + message_tokens, self.max_token_limit
                )
                and chat_messages
            ):
                # トークン数が最大を超える場合、ループを抜ける
                break
            role = cast(Literal["system", "user", "assistant"], message["role"])
            chat_messages.insert(0, ChatMessage(role=role, content=message["content"]))
            total_tokens += message_tokens

        if not any(message["role"] == "system" for message in chat_messages):
            chat_messages.insert(0, {"role": "system", "content": create_prompt()})

        return chat_messages

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
