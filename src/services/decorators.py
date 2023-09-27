from functools import wraps
from http import HTTPStatus
from typing import List

from pydantic import ValidationError

from src import logger
from src.schemas.responses import DataSchema, ResponseSchema
from src.utils.exceptions import Error400, Error403, Error503


def action(allowed_methods: List[str]):
    """
    Decorator that handles return success, clients 4xx error or server 5xx error.

    Args:
        allowed_methods (): HTTP method allowed for endpoint.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if args[0]["httpMethod"] not in allowed_methods:
                return ResponseSchema(status_code=405, body=DataSchema[dict](message="Method not allowed")).model_dump(
                    by_alias=True
                )

            try:
                return func(*args, **kwargs)

            except ValidationError as e:
                error_data = {"message": "", "data": []}
                for error in e.errors():
                    error_detail = {
                        "field": error["loc"],
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    error_data["data"].append(error_detail)

                    if error_detail["message"] not in error_data["message"]:
                        error_data["message"] += str(error_detail["message"]) + ". "

                error_data["message"] = error_data["message"].strip()

                error_data["data"] = error_data["data"][0] if len(error_data["data"]) == 1 else error_data["data"]
                return ResponseSchema(
                    status_code=HTTPStatus.BAD_REQUEST, body=DataSchema[type(error_data["data"])](**error_data)
                ).model_dump(by_alias=True)
            except Error400 as e:
                return ResponseSchema(
                    status_code=HTTPStatus.BAD_REQUEST, body=DataSchema[dict](message=str(e) or e.message)
                ).model_dump(by_alias=True)
            except Error403 as e:
                return ResponseSchema(
                    status_code=HTTPStatus.FORBIDDEN, body=DataSchema[dict](message=str(e) or e.message)
                ).model_dump(by_alias=True)
            except Error503 as e:
                return ResponseSchema(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE, body=DataSchema[dict](message=str(e) or e.message)
                ).model_dump(by_alias=True)
            except Exception:
                logger.error(f"error in {func.__name__}", exc_info=True)
                return ResponseSchema(
                    status_code=500, body=DataSchema[dict](message="Internal server error")
                ).model_dump(by_alias=True)

        return inner

    return wrapper
