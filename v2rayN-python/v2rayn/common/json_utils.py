"""JSON utility functions.

Ported from ServiceLib/Common/JsonUtils.cs.
Uses Python's built-in json module.
"""

from __future__ import annotations

import copy
import json
from typing import Any, TypeVar

from v2rayn.common import logging_config

T = TypeVar("T")

_tag = "JsonUtils"


def deep_copy(obj: Any) -> Any:
    """Deep copy an object via JSON serialization."""
    if obj is None:
        return None
    try:
        return copy.deepcopy(obj)
    except Exception:
        # Fallback to JSON roundtrip
        return deserialize(serialize(obj, indented=False))


def deserialize(str_json: str | None, cls: type[T] | None = None) -> T | dict | None:
    """Deserialize JSON string to object.

    Args:
        str_json: JSON string to deserialize
        cls: Optional class to deserialize into (must be a dataclass)

    Returns:
        Deserialized object, dict, or None
    """
    try:
        if not str_json or not str_json.strip():
            return None
        data = json.loads(str_json)
        if cls is not None:
            return _dict_to_dataclass(cls, data)
        return data
    except (json.JSONDecodeError, Exception):
        return None


def parse_json(str_json: str | None) -> Any:
    """Parse JSON string to a Python object (dict/list).

    Args:
        str_json: JSON string to parse

    Returns:
        Parsed JSON object or None
    """
    try:
        if not str_json or not str_json.strip():
            return None
        return json.loads(str_json)
    except (json.JSONDecodeError, Exception):
        return None


def serialize(obj: Any, indented: bool = True, null_value: bool = False) -> str:
    """Serialize object to JSON string.

    Args:
        obj: Object to serialize
        indented: Whether to indent the output
        null_value: Whether to include null values

    Returns:
        JSON string
    """
    try:
        if obj is None:
            return ""

        indent = 2 if indented else None

        if hasattr(obj, "__dataclass_fields__"):
            data = _dataclass_to_dict(obj, include_none=null_value)
        elif hasattr(obj, "__dict__"):
            data = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            if not null_value:
                data = {k: v for k, v in data.items() if v is not None}
        else:
            data = obj

        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def _dataclass_to_dict(obj: Any, include_none: bool = False) -> dict:
    """Convert a dataclass instance to a dict."""
    if not hasattr(obj, "__dataclass_fields__"):
        return obj

    result = {}
    for field_name in obj.__dataclass_fields__:
        if field_name.startswith("_"):
            continue
        value = getattr(obj, field_name)
        if value is None and not include_none:
            continue
        if hasattr(value, "__dataclass_fields__"):
            value = _dataclass_to_dict(value, include_none)
        elif isinstance(value, list):
            value = [
                _dataclass_to_dict(v, include_none) if hasattr(v, "__dataclass_fields__") else v for v in value
            ]
        elif isinstance(value, dict):
            value = {
                k: _dataclass_to_dict(v, include_none) if hasattr(v, "__dataclass_fields__") else v
                for k, v in value.items()
            }
        result[field_name] = value
    return result


def _dict_to_dataclass(cls: type[T], data: dict) -> T:
    """Convert a dict to a dataclass instance."""
    import dataclasses

    if not dataclasses.is_dataclass(cls) or not isinstance(data, dict):
        return data  # type: ignore

    field_names = {f.name for f in dataclasses.fields(cls)}
    filtered = {}
    for k, v in data.items():
        if k in field_names:
            field_info = next(f for f in dataclasses.fields(cls) if f.name == k)
            # Basic type conversion for nested dataclasses would go here
            filtered[k] = v
    return cls(**filtered)
