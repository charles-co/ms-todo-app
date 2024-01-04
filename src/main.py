import re
from http import HTTPMethod, HTTPStatus
from typing import Any

from docs import index
from src.config.settings import get_settings
from src.schemas.responses import DataSchema, ResponseSchema
from src.services import todo

from . import logger

settings = get_settings()


def todo_app_gateway_handler(event: dict[str, Any], context: object):
    router = {
        r"^(?:\/staging|test|dev|prod)?\/todos\/(?P<id>[a-zA-Z0-9]+)$": {
            HTTPMethod.GET: todo.get_todo,
            HTTPMethod.DELETE: todo.delete_todo,
            HTTPMethod.PATCH: todo.update_todo_partial,
        },
        r"^(?:\/staging|test|dev|prod)?\/todos(?:\?[^/]+)?$": {
            HTTPMethod.GET: todo.get_todos,
            HTTPMethod.POST: todo.create_todo,
        },
    }

    # Add docs routes if not in production
    router |= {
        r"^(?:\/staging|test|dev)?\/docs\/(?P<filename>redoc-static.html|swagger-doc.html)(?:#.*)?$": {
            HTTPMethod.GET: index.get_doc,
        },
    }

    for route, handlers in router.items():
        if match := re.match(route, event["path"]):
            logger.info(
                (
                    f"Request -----> {event['httpMethod']} {event['path']} - "
                    + f"Path: {event['requestContext'].get('pathParameters')}, "
                    + f"Query: {event['requestContext'].get('queryStringParameters')}"
                    + f"\n\nEvent: {event}\n\nContext: {context}"
                )
            )
            if match.groupdict():
                event["pathParameters"] = match.groupdict()

            if handler := handlers.get(event["httpMethod"]):
                logger.info(f"Handler -----> {handler.__name__}")
                return handler(event, context)

    return ResponseSchema(
        status_code=HTTPStatus.NOT_FOUND, body=DataSchema[dict](message=HTTPStatus.NOT_FOUND.description)
    ).model_dump_json(by_alias=True)
