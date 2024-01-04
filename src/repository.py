import datetime
from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key
from pydantic import validate_call

from src.config.settings import get_settings
from src.db import DynamoDB

from . import logger

settings = get_settings()


class TodoAppRepository:
    @classmethod
    @validate_call
    def create(cls, *, item: dict[str, Any]) -> bool:
        try:
            resp = DynamoDB(
                table_name=settings.TODO_APP_DB,
            ).put_item(
                item=item,
            )
        except Exception as e:
            logger.error(f"Error in {cls.__name__}", exc_info=True)
            raise e
        return resp

    @classmethod
    @validate_call
    def exists(cls, *, pk: str, **kwargs) -> bool:
        if (
            DynamoDB(table_name=settings.TODO_APP_DB).count(
                KeyConditionExpression=Key(settings.TODO_APP_DB_PK).eq(pk),
                **kwargs,
            )
        ) >= 1:
            return True
        return False

    @classmethod
    def get(cls, *, pk: str, **kwargs) -> dict[str, Any]:
        """Get todo item by primary key.

        Args:
            pk (str): Primary key of todo. `id`

        Returns:
            dict[str, Any]: Return todo object if found, otherwise None
        """
        item = DynamoDB(table_name=settings.TODO_APP_DB).get_item(
            key={settings.TODO_APP_DB_PK: pk},
            **kwargs,
        )

        return item

    @classmethod
    def filter(cls, **kwargs) -> dict[str, Any]:
        """Get filtered todos"""
        items = (
            DynamoDB(table_name=settings.TODO_APP_DB)
            .scan(
                **kwargs,
            )
            .get("Items")
        )
        return items

    @classmethod
    @validate_call
    def delete(cls, *, pk: str) -> None:
        return DynamoDB(table_name=settings.TODO_APP_DB).delete_item(
            key={settings.TODO_APP_DB_PK: pk},
        )

    @classmethod
    @validate_call
    def update(
        cls,
        *,
        pk: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        if not data:
            return {}

        expression_attribute_values = {}
        expression_attribute_names = {}

        update_expression = "SET #updated_at_proxy = :updated_at,"
        expression_attribute_values[":updated_at"] = Decimal(datetime.datetime.now().timestamp())
        expression_attribute_names["#updated_at_proxy"] = "updated_at"

        for key, value in data.items():
            expression_attribute_names[f"#{key}_proxy"] = key
            update_expression += f"#{key}_proxy = :{key},"
            expression_attribute_values[f":{key}"] = value

        return DynamoDB(table_name=settings.TODO_APP_DB).update_item(
            key={settings.TODO_APP_DB_PK: pk},
            UpdateExpression=update_expression.rstrip(", "),
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
        )
