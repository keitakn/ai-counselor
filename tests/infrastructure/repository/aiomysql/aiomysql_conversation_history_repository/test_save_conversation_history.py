import pytest
from typing import Tuple
from aiomysql import Connection
from tests.db.create_and_setup_db_connection import create_and_setup_db_connection
from infrastructure.repository.aiomysql.aiomysql_conversation_history_repository import (
    AiomysqlConversationHistoryRepository,
    SaveConversationHistoryDto,
)


@pytest.fixture
async def create_test_db_connection() -> Tuple[Connection, str]:
    connection, test_db_name = await create_and_setup_db_connection()

    async with connection.cursor() as cursor:
        await cursor.execute("TRUNCATE TABLE conversation_histories")
    await connection.commit()

    return connection, test_db_name


@pytest.mark.asyncio
async def test_save_conversation_history(create_test_db_connection):
    connection, test_db_name = await create_test_db_connection

    user_id = "Ua000xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    dto = SaveConversationHistoryDto(
        user_id=user_id,
        user_message="こんにちは私の悩みを聞いてください。",
        ai_message="こんにちは。お話しできることを嬉しく思います。どのようなことでお悩みですか？",
    )

    repository = AiomysqlConversationHistoryRepository(connection)

    await repository.save_conversation_history(dto)

    async with connection.cursor() as cursor:
        sql = """
        SELECT *
        FROM conversation_histories
        WHERE user_id = %s
        """

        await cursor.execute(sql, user_id)
        result = await cursor.fetchone()

    assert result is not None
    assert result["user_id"] == user_id
    assert result["user_message"] == dto.get("user_message")
    assert result["ai_message"] == dto.get("ai_message")
