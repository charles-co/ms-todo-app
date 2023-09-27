from datetime import datetime
from decimal import Decimal

import pytz
from annotated_types import Gt
from pydantic import WithJsonSchema
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


def normalize_datetime(v: Decimal) -> str:
    return datetime.fromtimestamp(float(v), tz=pytz.utc).isoformat()


def normlize_decimal_to_int(v: Decimal) -> int:
    return int(v)


def convert_datetime_to_decimal(v):
    if isinstance(v, datetime):
        v = Decimal(v.astimezone(tz=pytz.utc).timestamp())
    return v


DateTime = Annotated[
    Decimal,
    Gt(0),
    PlainSerializer(lambda v: normalize_datetime(v), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

DateTimeDB = Annotated[Decimal, BeforeValidator(convert_datetime_to_decimal), Gt(0)]
