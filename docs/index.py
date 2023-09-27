import html
from http import HTTPStatus
from pathlib import Path
from typing import Any

from src.config.settings import get_settings
from src.schemas.responses import DataSchema, ResponseSchema

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": True,
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT",
    "Access-Control-Allow-Headers": "*",
    "Content-Type": "text/html",
}


def get_doc(event: dict[str, Any], context: object):
    try:
        data = html.unescape((BASE_DIR / event["pathParameters"]["filename"]).read_text())
    except Exception:
        return ResponseSchema(
            status_code=HTTPStatus.NOT_FOUND, body=DataSchema[dict](message=HTTPStatus.NOT_FOUND.description)
        ).model_dump(by_alias=True)

    return {
        "statusCode": HTTPStatus.OK,
        "body": data,
        "headers": HEADERS,
    }
