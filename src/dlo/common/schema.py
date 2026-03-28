from enum import Enum

from pydantic import BaseModel, ConfigDict


class EnumBase(str, Enum):
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


class SchemaBase(BaseModel):
    """Base model configuration"""

    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
        validate_by_name=True,
    )