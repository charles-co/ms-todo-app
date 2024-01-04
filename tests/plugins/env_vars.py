import os

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args, early_config, parser):
    os.environ["STAGE"] = "test"
    os.environ["TODO_APP_DB"] = "ms-todo-app"
    os.environ["TODO_APP_DB_PK"] = "id"
    os.environ["TODO_APP_DB_SK"] = "updated_at"
