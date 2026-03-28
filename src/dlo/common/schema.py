from dataclasses import dataclass
from enum import StrEnum

from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import SerializableType


class EnumBase(SerializableType, StrEnum):
    """
    Base enum for semantic specs.

    - Case-insensitive parsing
    - Canonical lowercase values
    - YAML / JSON friendly
    """

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None

    @classmethod
    def values(cls) -> list[str]:
        """Return all allowed enum values."""
        return [member.value for member in cls]

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Check if a value is a valid enum value."""
        return value.lower() in cls.values()

    def __str__(self) -> str:
        return self.value

    # https://docs.python.org/3.6/library/enum.html#using-automatic-values
    def _generate_next_value_(name, *_):
        return name

    def _serialize(self) -> str:
        return self.value

    @classmethod
    def _deserialize(cls, value: str):
        return cls(value)


@dataclass
class SchemaMixin(DataClassJSONMixin): ...
