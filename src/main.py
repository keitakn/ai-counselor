import uvicorn
import os
from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from presentation.router import health_checks
from presentation.router import messages
from pydantic_core import ValidationError
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from infrastructure.repository.openai.openai_generate_message_repository import (
    OpenAiGenerateMessageRepository,
)
from usecase.generate_message_use_case import (
    GenerateMessageUseCaseDto,
    GenerateMessageUseCaseResult,
    GenerateMessageUseCase,
)

app = FastAPI(
    title="ai-counselor",
)


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
def unauthorized_exception_handler(
    request: Request, exception: HTTPException
) -> JSONResponse:
    return JSONResponse(
        content={
            "type": "UNAUTHORIZED",
            "title": "invalid Authorization Header.",
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
def not_found_exception_handler(
    request: Request, exception: HTTPException
) -> JSONResponse:
    return JSONResponse(
        content={
            "type": "NOT_FOUND",
            "title": "Resource not found.",
            "detail": f"{str(request.url)} not found.",
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    invalid_params = []

    errors = exc.errors()

    for error in errors:
        invalid_params.append({"name": error["loc"][1], "reason": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "type": "UNPROCESSABLE_ENTITY",
                "title": "validation Error.",
                "invalidParams": invalid_params,
            }
        ),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    invalid_params = []

    errors = exc.errors()

    for error in errors:
        invalid_params.append({"name": error["loc"][0], "reason": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "type": "UNPROCESSABLE_ENTITY",
                "title": "validation Error.",
                "invalidParams": invalid_params,
            }
        ),
    )


app.include_router(health_checks.router)
app.include_router(messages.router)

channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

configuration = Configuration(access_token=channel_access_token)

async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


@app.post("/v1/line/callback")
async def handle_callback(request: Request):
    signature = request.headers["X-Line-Signature"]

    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="申し訳ありません。テキストメッセージ以外は理解できません。")],
                )
            )
            continue

        generate_message_repository = OpenAiGenerateMessageRepository()

        if event.source is not None:
            if event.source.type == "user" and isinstance(event.source.user_id, str):
                user_id = event.source.user_id

                dto = GenerateMessageUseCaseDto(
                    request_id=event.webhook_event_id,
                    user_id=user_id,
                    message=event.message.text,
                    generate_message_repository=generate_message_repository,
                )

                use_case = GenerateMessageUseCase(dto)

                use_case_result: GenerateMessageUseCaseResult = await use_case.execute()

                response_message = use_case_result.get("message")

                await line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=response_message)],
                    )
                )

    return "OK"


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
