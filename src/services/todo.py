import json
from functools import reduce
from http import HTTPMethod, HTTPStatus
from typing import Any

from boto3.dynamodb.conditions import Attr

from src.config.settings import get_settings
from src.repository import TodoAppRepository
from src.schemas.db import TodoDBSchema
from src.schemas.requests import TodoCreateRequestSchema, TodoUpdateRequestSchema
from src.schemas.responses import DataSchema, ResponseSchema, TodoResponseSchema
from src.services.decorators import action
from src.utils.exceptions import TodoDoesNotExist

settings = get_settings()


@action(allowed_methods=[HTTPMethod.GET])
def get_todo(event: dict[str, Any], context: object):
    data = TodoAppRepository.get(pk=event["pathParameters"]["id"])
    if not data:
        raise TodoDoesNotExist
    return ResponseSchema(
        status_code=HTTPStatus.OK, body=DataSchema[TodoResponseSchema](message=HTTPStatus.OK.description, data=data)
    ).model_dump(by_alias=True)


@action(allowed_methods=[HTTPMethod.GET])
def get_todos(event: dict[str, Any], context: object):
    _filter = []
    kwargs = {}

    if qs := event.get("queryStringParameters"):
        if (is_completed := qs.get("isCompleted")) and is_completed.title() in ["True", "False"]:
            _filter.append(Attr("is_completed").eq(is_completed.title() == "True"))

        if (is_pinned := qs.get("isPinned")) and is_pinned.title() in ["True", "False"]:
            _filter.append(Attr("is_pinned").eq(is_pinned.title() == "True"))

    if _filter:
        kwargs["FilterExpression"] = reduce(lambda x, y: x & y, _filter)
    data = TodoAppRepository.get(pk=None, **kwargs)

    return ResponseSchema(
        status_code=HTTPStatus.OK, body=DataSchema[TodoResponseSchema](message=HTTPStatus.OK.description, data=data)
    ).model_dump(by_alias=True)


@action(allowed_methods=[HTTPMethod.DELETE])
def delete_todo(event: dict[str, Any], context: object):
    TodoAppRepository.delete(pk=event["pathParameters"]["id"])
    return ResponseSchema(
        status_code=HTTPStatus.NO_CONTENT, body=DataSchema[dict](message=HTTPStatus.NO_CONTENT.description)
    ).model_dump(by_alias=True)


@action(allowed_methods=[HTTPMethod.POST])
def create_todo(event: dict[str, Any], context: object):
    _inital_data = TodoCreateRequestSchema.model_validate(json.loads(event["body"])).model_dump()

    obj = TodoDBSchema.model_validate(_inital_data).model_dump()

    data = TodoAppRepository.create(item=obj)
    return ResponseSchema(
        status_code=HTTPStatus.CREATED,
        body=DataSchema[TodoResponseSchema](message=HTTPStatus.CREATED.description, data=data),
    ).model_dump(by_alias=True)


@action(allowed_methods=[HTTPMethod.PATCH])
def update_todo_partial(event: dict[str, Any], context: object):
    if TodoAppRepository.exists(pk=event["pathParameters"]["id"]) is False:
        raise TodoDoesNotExist

    _inital_data = TodoUpdateRequestSchema.model_validate(json.loads(event["body"])).model_dump(exclude_none=True)

    data = TodoAppRepository.update(pk=event["pathParameters"]["id"], data=_inital_data)
    return ResponseSchema(
        status_code=HTTPStatus.OK, body=DataSchema[TodoResponseSchema](message=HTTPStatus.OK.description, data=data)
    ).model_dump(by_alias=True)
