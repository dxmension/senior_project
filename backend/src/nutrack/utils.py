from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    ok: bool = True
    data: DataT | None = None
    meta: dict[str, Any] | None = None


class ApiErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ApiErrorPayload
