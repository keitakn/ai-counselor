from typing import TypedDict, Protocol


class SaveConversationHistoryDto(TypedDict):
    user_id: str
    user_message: str
    ai_message: str


class ConversationHistoryRepositoryInterface(Protocol):
    async def save_conversation_history(self, dto: SaveConversationHistoryDto) -> None:
        ...
