from typing import TypedDict, Protocol, List
from domain.message import ChatMessage


class CreateMessagesWithConversationHistoryDto(TypedDict):
    user_id: str
    request_message: str


class SaveConversationHistoryDto(TypedDict):
    user_id: str
    user_message: str
    ai_message: str


class ConversationHistoryRepositoryInterface(Protocol):
    async def create_messages_with_conversation_history(
        self, dto: CreateMessagesWithConversationHistoryDto
    ) -> List[ChatMessage]:
        ...

    async def save_conversation_history(self, dto: SaveConversationHistoryDto) -> None:
        ...
