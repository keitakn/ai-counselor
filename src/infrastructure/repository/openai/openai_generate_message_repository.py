import os
from typing import cast, List
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from domain.repository.generate_message_repository_interface import (
    GenerateMessageRepositoryInterface,
    GenerateMessageRepositoryDto,
    GenerateMessageResult,
)


class OpenAiGenerateMessageRepository(GenerateMessageRepositoryInterface):
    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        self.client = AsyncOpenAI(api_key=self.OPENAI_API_KEY)

    async def generate_message(
        self, dto: GenerateMessageRepositoryDto
    ) -> GenerateMessageResult:
        messages = cast(List[ChatCompletionMessageParam], dto.get("chat_messages"))
        user_id = str(dto.get("user_id"))

        response = await self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.7,
            user=user_id,
        )

        ai_response_id = response.id

        return {
            "ai_response_id": ai_response_id,
            "message": str(response.choices[0].message.content),
        }
