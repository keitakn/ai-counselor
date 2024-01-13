from typing import Protocol, TypedDict


class GenerateMessageRepositoryDto(TypedDict):
    user_id: str
    message: str


class GenerateMessageResult(TypedDict):
    ai_response_id: str
    message: str


class GenerateMessageRepositoryInterface(Protocol):
    async def generate_message(
        self, dto: GenerateMessageRepositoryDto
    ) -> GenerateMessageResult:
        ...
