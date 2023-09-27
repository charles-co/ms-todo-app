from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    STAGE: str

    TODO_APP_DB: str
    TODO_APP_DB_PK: str
    TODO_APP_DB_SK: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
