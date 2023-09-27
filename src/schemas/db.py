import datetime
import uuid
from decimal import Decimal
from functools import partial
from typing import Optional

import pytz
from pydantic import BaseModel, Field, computed_field

from src.config.settings import get_settings
from src.fields import DateTimeDB

settings = get_settings()
now: Decimal = partial(Decimal, datetime.datetime.now(pytz.utc).timestamp())


class TimeStampedDBBaseModel(BaseModel):
    created_at: Optional[DateTimeDB] = now()

    @computed_field(return_type=Decimal)
    def updated_at(self):
        updated_at = Decimal(datetime.datetime.now(pytz.utc).timestamp())
        return updated_at if updated_at >= self.created_at else self.created_at


class TodoDBSchema(TimeStampedDBBaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4().hex))
    title: str
    description: str
    is_completed: bool = False
    is_pinned: bool = False
