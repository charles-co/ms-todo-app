from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TodoCreateRequestSchema(BaseModel):
    title: str
    description: str
    is_completed: Optional[bool] = False
    is_pinned: Optional[bool] = False

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TodoUpdateRequestSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    is_pinned: Optional[bool] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
