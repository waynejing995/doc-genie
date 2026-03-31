"""Sample Python file for testing."""

import os
from typing import List


def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"


class UserService:
    """User service class."""

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(user_id)