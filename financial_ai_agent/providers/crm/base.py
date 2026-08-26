from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCRMProvider(ABC):
    def __init__(self, connector):
        self.connector = connector

    @abstractmethod
    def search(self, object_type: str, query=None, filters=None, limit=20) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get(self, object_type: str, record_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def create(self, object_type: str, values: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def update(self, object_type: str, record_id: str, values: dict) -> dict:
        raise NotImplementedError

    def create_note(self, object_type: str, record_id: str, note: str) -> dict:
        raise NotImplementedError

    def create_task(self, values: dict) -> dict:
        return self.create("Task", values)

    def activity_history(self, object_type: str, record_id: str) -> list[dict]:
        return []

    @abstractmethod
    def test_connection(self) -> dict[str, Any]:
        raise NotImplementedError

