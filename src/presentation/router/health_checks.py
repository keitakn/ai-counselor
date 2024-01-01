from fastapi import APIRouter
from pydantic import BaseModel
from http import HTTPStatus
from starlette.responses import JSONResponse

router = APIRouter()


class HealthCheckJsonResponse(BaseModel):
    status: str = "ok"


@router.get("/v1/health-checks", response_model=HealthCheckJsonResponse)
async def health_checks() -> JSONResponse:
    """
    healthCheck用のエンドポイントです。\n
    正常な場合、`{"status": "ok"}`を返します。
    """
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"status": "ok"},
    )
