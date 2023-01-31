from enum import Enum


class BasicEnum(str, Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
