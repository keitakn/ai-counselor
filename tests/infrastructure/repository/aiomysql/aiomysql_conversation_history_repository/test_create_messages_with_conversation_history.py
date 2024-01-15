import pytest
from typing import Tuple
from aiomysql import Connection
from tests.db.create_and_setup_db_connection import create_and_setup_db_connection
from infrastructure.repository.aiomysql.aiomysql_conversation_history_repository import (
    AiomysqlConversationHistoryRepository,
    CreateMessagesWithConversationHistoryDto,
)
from domain.prompt import create_prompt


@pytest.fixture
async def create_test_db_connection() -> Tuple[Connection, str]:
    connection, test_db_name = await create_and_setup_db_connection()

    async with connection.cursor() as cursor:
        await cursor.execute("TRUNCATE TABLE conversation_histories")

        await cursor.executemany(
            """
            INSERT INTO
              conversation_histories
              (user_id, user_message, ai_message)
            VALUES
              (%s, %s, %s)
            """,
            [
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗1",
                    "もちろんです。何でもお話ください❗1",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗2",
                    "もちろんです。何でもお話ください❗2",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗3",
                    "もちろんです。何でもお話ください❗3",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗4",
                    "もちろんです。何でもお話ください❗4",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗5",
                    "もちろんです。何でもお話ください❗5",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗6",
                    "もちろんです。何でもお話ください❗6",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗7",
                    "もちろんです。何でもお話ください❗7",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗8",
                    "もちろんです。何でもお話ください❗8",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗9",
                    "もちろんです。何でもお話ください❗9",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗10",
                    "もちろんです。何でもお話ください❗10",
                ),
                (
                    "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001",
                    "こんにちは、私の悩みを聞いてください❗11",
                    "もちろんです。何でもお話ください❗11",
                ),
            ],
        )
    await connection.commit()

    return connection, test_db_name


@pytest.mark.asyncio
async def test_create_messages_with_conversation_history(create_test_db_connection):
    connection, test_db_name = await create_test_db_connection

    user_id = "Uaxxxxxxxxxxxxxxxxxxxxxxxxxxx0001"

    dto = CreateMessagesWithConversationHistoryDto(
        user_id=user_id,
        request_message="おはようございます。私の相談相手になって欲しいです。",
    )

    repository = AiomysqlConversationHistoryRepository(connection, 1000)

    chat_messages = await repository.create_messages_with_conversation_history(dto)

    expected = [
        {"role": "system", "content": create_prompt()},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗2"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗2"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗3"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗3"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗4"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗4"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗5"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗5"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗6"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗6"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗7"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗7"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗8"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗8"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗9"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗9"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗10"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗10"},
        {"role": "user", "content": "こんにちは、私の悩みを聞いてください❗11"},
        {"role": "assistant", "content": "もちろんです。何でもお話ください❗11"},
        {"role": "user", "content": "おはようございます。私の相談相手になって欲しいです。"},
    ]

    assert expected == chat_messages
