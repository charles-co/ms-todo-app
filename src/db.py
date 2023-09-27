import boto3

from src.config.settings import get_settings

settings = get_settings()


class DynamoDB:
    kwargs = {
        "region_name": "us-east-1",
        "service_name": "dynamodb",
    } | (
        {
            "region_name": "localhost",
            "endpoint_url": "http://localhost:8000",
            "aws_access_key_id": "dev",
            "aws_secret_access_key": "dev",
        }
        if settings.STAGE == "dev"
        else {}
    )

    dynamodb_resource = boto3.resource(**kwargs)
    dynamodb_client = boto3.client(**kwargs)

    def __init__(self, table_name):
        self._table = self.dynamodb_resource.Table(table_name)

    def get_item(self, key, **kwargs):
        return self._table.get_item(Key=key, **kwargs).get("Item")

    def query(self, key_condition_expression, **kwargs):
        return self._table.query(
            KeyConditionExpression=key_condition_expression,
            **kwargs,
        )

    def scan(self, **kwargs):
        return self._table.scan(
            **kwargs,
        )

    def put_item(self, item):
        resp = self._table.put_item(Item=item)
        if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise ConnectionRefusedError

        mappings = {
            settings.TODO_APP_DB: {
                "KeyConditionExpression": f"{settings.TODO_APP_DB_PK} = :pk",
                "ExpressionAttributeValues": {":pk": item[settings.TODO_APP_DB_PK]},
            }
        }
        res = self.query(
            key_condition_expression=mappings[self._table.name]["KeyConditionExpression"],
            ExpressionAttributeValues=mappings[self._table.name]["ExpressionAttributeValues"],
        ).get("Items", [])
        return [{}, res[0]][len(res) > 0]

    def update_item(self, key, **kwargs):
        resp = self._table.update_item(
            Key=key,
            **kwargs,
            ReturnValues="ALL_NEW",
        )
        if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise ConnectionRefusedError
        return resp["Attributes"]

    def delete_item(self, key):
        return self._table.delete_item(Key=key)

    def count(self, **kwargs):
        return self._table.query(
            **kwargs,
            Select="COUNT",
        ).get("Count", 0)
