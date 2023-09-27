import json
from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel

from src.config.settings import get_settings
from src.fields import DateTime

DataT = TypeVar("DataT")

settings = get_settings()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": True,
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT",
    "Access-Control-Allow-Headers": "*",
}


class DataSchema(BaseModel, Generic[DataT]):
    meta: Optional[dict[str, Any]] = None
    message: str
    data: Optional[Union[DataT, List[DataT]]] = None

    @classmethod
    def __concrete_name__(cls: type[Any], params: tuple[type[Any], ...]) -> str:
        if hasattr(params[0], "__name__"):
            return f"{params[0].__name__.title()} DataSchema"
        return "DataSchema"


class ResponseSchema(BaseModel):
    body: Union[BaseModel, Any]
    status_code: int
    headers: Optional[dict[str, Any]] = CORS_HEADERS

    @field_serializer("body", return_type=str)
    def serialize_body(self, v):
        if isinstance(v, BaseModel):
            # NOTE: This is a hack to exclude fields that are None from the response.
            to_exclude = {}
            for key in ["meta", "data"]:
                if getattr(v, key) is None:
                    to_exclude[key] = True
            return v.model_dump_json(by_alias=True, exclude=to_exclude)
        return json.dumps(v)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TodoResponseSchema(BaseModel):
    id: str
    title: str
    description: str
    is_completed: bool
    is_pinned: bool
    created_at: DateTime
    updated_at: DateTime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
