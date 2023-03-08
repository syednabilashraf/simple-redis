from dataclasses import dataclass
from time import time
from typing import Optional


@dataclass
class Value:
    value: str
    expires_at: Optional[int]


class KeyValueStore:
    store: dict[str, Value]

    def __init__(self) -> None:
        self.store = {}

    def set(self, key: str, value: str, *,
            expires_at: Optional[int] = None) -> None:
        self.store[key] = Value(value, expires_at)

    def get(self, key: str) -> Optional[str]:
        if key not in self.store:
            return None
        value = self.store[key]
        if value.expires_at is not None and value.expires_at < int(time() * 1000):
            del self.store[key]
            return None
        return value.value
