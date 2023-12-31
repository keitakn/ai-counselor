import os
from openai import AsyncOpenAI
from domain.repository.generate_message_repository_interface import (
    GenerateMessageRepositoryInterface,
    GenerateMessageRepositoryDto,
    GenerateMessageResult,
)
from domain.prompt import create_prompt


class OpenAiGenerateMessageRepository(GenerateMessageRepositoryInterface):
    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        self.client = AsyncOpenAI(api_key=self.OPENAI_API_KEY)

    async def generate_message(
        self, dto: GenerateMessageRepositoryDto
    ) -> GenerateMessageResult:
        user = str(dto.get("conversation_id"))

        response = await self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": create_prompt()},
                {
                    "role": "user",
                    "content": dto.get("message"),
                },
            ],
            temperature=0.7,
            user=user,
        )

        ai_response_id = response.id

        return {
            "ai_response_id": ai_response_id,
            "message": str(response.choices[0].message.content),
        }
