from typing import Protocol, TypedDict, List
from domain.message import ChatMessage


class GenerateMessageRepositoryDto(TypedDict):
    user_id: str
    chat_messages: List[ChatMessage]


class GenerateMessageResult(TypedDict):
    ai_response_id: str
    message: str


class GenerateMessageRepositoryInterface(Protocol):
    async def generate_message(
        self, dto: GenerateMessageRepositoryDto
    ) -> GenerateMessageResult:
        ...
