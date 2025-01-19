from typing import Dict


class InMemoryDatabase:
    def __init__(self):
        self.cache = {}

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: Dict):
        self.cache[key] = value