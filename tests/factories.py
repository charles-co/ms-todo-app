import datetime

import pytz
from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory

from src.schemas.db import TodoDBSchema


class TodoDBSchemaFactory(ModelFactory[TodoDBSchema]):
    __model__ = TodoDBSchema

    is_completed: bool = False
    is_pinned: bool = False

    @classmethod
    def id(cls) -> str:
        return cls.__faker__.uuid4(cast_to=None).hex

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.text(max_nb_chars=5)

    @classmethod
    def description(cls) -> str:
        return cls.__faker__.paragraph(nb_sentences=5)

    @classmethod
    def created_at(cls) -> datetime.datetime:
        return cls.__faker__.date_time_between(tzinfo=pytz.utc, start_date="-7d", end_date="-1d")

    @post_generated
    @classmethod
    def updated_at(cls, created_at) -> datetime.datetime:
        return cls.__faker__.date_time_between(tzinfo=pytz.utc, start_date=created_at, end_date="now")
