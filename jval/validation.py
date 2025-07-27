"""
Defines the validation logic for the JVAL schema.
"""

from typing import Any, Dict, Union

from .errors import raise_error

NotPresent = type(None)


SYMBOL_OPTIONAL = "?"
SYMBOL_DEFAULT = "_"
SYMBOL_TYPED = "*"


SYMBOL_TYPE_START = "<"
SYMBOL_TYPE_END = ">"


def _validate(
    json_dict: Any,
    jval_schema: Dict[str, Any],
    __context: str = "",
    *,
    drop_extra_keys: bool = False,
) -> Any:
    """
    Validate JSON data against the JVAL schema.

    Args:
        json_dict (Any):
            JSON data to validate.
        jval_schema (Dict[str, Any]):
            JVAL schema to validate against.
        drop_extra_keys (bool, optional):
            Drop extra keys in the JSON data that are not defined in the JVAL schema.
            Defaults to False.

    Returns:
        Validated JSON data.
    """
    validated_data = {}

    for schema_key, schema_value in jval_schema.items():
        clean_key = get_clean_key(schema_key)
        actual_value = json_dict.get(clean_key, NotPresent)
        current_context = f"{__context}.{clean_key}" if __context else clean_key
        schema_value = None if schema_value in ({}, []) else schema_value

        # Recursively validate nested objects
        if isinstance(actual_value, dict) and isinstance(schema_value, dict):
            _validate(
                actual_value,
                schema_value,
                current_context,
                drop_extra_keys=drop_extra_keys,
            )
            validated_data[clean_key] = actual_value

        # Recursively validate nested lists
        elif isinstance(actual_value, list) and isinstance(schema_value, list):
            _validate_list(
                schema_key,
                schema_value,
                actual_value,
                current_context,
                drop_extra_keys=drop_extra_keys,
            )
            validated_data[clean_key] = actual_value

        # Validate literals, types, and optional values
        else:

            # Actual value exists
            if actual_value is not NotPresent:
                # Value is a type definition
                if (
                    isinstance(schema_value, str)
                    and schema_value.startswith(SYMBOL_TYPE_START)
                    and schema_value.endswith(SYMBOL_TYPE_END)
                ):
                    _validate_type(
                        schema_key,
                        schema_value,
                        actual_value,
                        current_context,
                    )

                # Spec key starts with an asterisk (type definition)
                elif schema_key.startswith(f"{SYMBOL_TYPED}"):
                    _validate_type(
                        schema_key,
                        schema_value,
                        actual_value,
                        current_context,
                    )

                # Spec key starts with a question mark (optional value)
                elif schema_key.startswith(f"{SYMBOL_OPTIONAL}"):
                    _validate_optional(
                        schema_key,
                        schema_value,
                        actual_value,
                        current_context,
                        drop_extra_keys=drop_extra_keys,
                    )

                # Spec key is a literal value
                else:
                    _validate_literal(
                        schema_key,
                        schema_value,
                        actual_value,
                        current_context,
                    )
                validated_data[clean_key] = actual_value

            # Actual value does not exist, but schema defines a default value
            elif schema_key.startswith(f"{SYMBOL_OPTIONAL}"):
                if schema_key.startswith(f"{SYMBOL_OPTIONAL}{SYMBOL_DEFAULT}"):
                    validated_data[clean_key] = schema_value

            # Actual value does not exist, and schema does not define a default value, raise error
            else:
                raise_error(clean_key, "missing value", current_context)

    # Extract clean keys from the JVAL schema
    schema_keys = {get_clean_key(k) for k in jval_schema}
    extra_keys = set(json_dict) - schema_keys

    # Handle extra keys in the JSON data
    for key in extra_keys:
        if drop_extra_keys:
            json_dict.pop(key)
        else:
            raise_error(key, "extra key not defined in schema", __context)

    return validated_data


def _validate_literal(
    key: str, schema_value: Any, actual_value: Any, current_context: str
):
    if actual_value != schema_value:
        raise_error(
            get_clean_key(key), f"expected literal '{schema_value}'", current_context
        )


def _validate_type(
    key: str,
    schema_value: str,
    actual_value: Any,
    current_context: str,
):
    if not isinstance(schema_value, str):
        return
    
    schema_type = (schema_value
                   .removeprefix(SYMBOL_TYPE_START)
                   .removesuffix(SYMBOL_TYPE_END))
    is_optional = schema_type.startswith("?")
    clean_schema_type = schema_type.removeprefix("?")

    type_dict = {
        "str": str,
        "int": int,
        "bool": bool,
        "float": float,
    }

    # Unknown type
    if clean_schema_type not in type_dict:
        raise_error(
            get_clean_key(key),
            f"unknown type {schema_value} in schema",
            current_context,
        )

    # Optional type
    if is_optional and actual_value is None:
        return

    # Check if the actual value is of the expected type
    expected_type = type_dict[clean_schema_type]
    if expected_type == float and isinstance(actual_value, (int, float)):
        return
    if not isinstance(actual_value, expected_type):
        raise_error(
            get_clean_key(key), f"expected type {schema_value}", current_context
        )


def _validate_optional(
    key: str,
    schema_value: Any,
    actual_value: Any,
    current_context: str,
    drop_extra_keys: bool = False,
):

    # Spec defines the type
    if key.startswith(f"{SYMBOL_OPTIONAL}{SYMBOL_TYPED}"):

        # Type is defined as literal
        if (
            isinstance(schema_value, str)
            and schema_value.startswith(f"{SYMBOL_TYPE_START}")
            and schema_value.endswith(f"{SYMBOL_TYPE_END}")
        ):
            _validate_type(key, schema_value, actual_value, current_context)

        # Type is defined as a list
        elif isinstance(schema_value, list):
            if not isinstance(actual_value, list):
                raise_error(get_clean_key(key), "expected a list", current_context)
            _validate_list(
                key,
                schema_value,
                actual_value,
                current_context,
                drop_extra_keys=drop_extra_keys,
            )

        # Type is defined as a dict
        elif isinstance(schema_value, dict):
            _validate(
                actual_value,
                schema_value,
                current_context,
                drop_extra_keys=drop_extra_keys,
            )

        # Type defined as a literal value
        else:
            _validate_literal(key, schema_value, actual_value, current_context)

    # Spec defines an value type implicitly by having a default value
    elif key.startswith(f"{SYMBOL_OPTIONAL}{SYMBOL_DEFAULT}"):
        _validate_type(
            key,
            f"{SYMBOL_TYPE_START}{type(schema_value).__name__}{SYMBOL_TYPE_END}",
            actual_value,
            current_context,
        )

    # Spec defined a literal value
    else:
        _validate_literal(key, schema_value, actual_value, current_context)


def _validate_list(
    key: str,
    schema_values: list,
    actual_values: Any,
    current_context: str,
    drop_extra_keys: bool = False,
):
    if not schema_values:
        if actual_values:
            raise_error(
                get_clean_key(key),
                "list mismatch: schema expects an empty list but JSON is not empty",
                current_context,
            )
        return

    # List of literals
    if isinstance(schema_values[0], (str, float, int)):
        is_typed_list = key.lstrip(SYMBOL_OPTIONAL).startswith(SYMBOL_TYPED)
        is_type_definition = (
            isinstance(schema_values[0], str)
            and schema_values[0].startswith(SYMBOL_TYPE_START)
            and schema_values[0].endswith(SYMBOL_TYPE_END)
        )

        # Literal represents a type definition
        if is_typed_list and is_type_definition:
            for index, actual_value in enumerate(actual_values):
                new_context = f"{current_context}[{index}]"
                _validate_type(key, schema_values[0], actual_value, new_context)

        # Literal represents a literal value
        else:
            if len(actual_values) != len(schema_values):
                raise_error(get_clean_key(key), "list length mismatch", current_context)
            for index, (actual_value, schema_value) in enumerate(
                zip(actual_values, schema_values)
            ):
                new_context = f"{current_context}[{index}]"
                _validate_literal(key, schema_value, actual_value, new_context)

    # List of dicts
    elif isinstance(schema_values[0], dict):
        for index, actual_value in enumerate(actual_values):
            new_context = f"{current_context}[{index}]"
            for schema in schema_values:
                _validate(
                    actual_value,
                    schema,
                    new_context,
                    drop_extra_keys=drop_extra_keys,
                )

    # List of lists
    elif isinstance(schema_values[0], list):
        for index, actual_value in enumerate(actual_values):
            new_context = f"{current_context}[{index}]"
            _validate_list(
                key,
                schema_values[0],
                actual_value,
                new_context,
                drop_extra_keys,
            )


def raise_if_invalid_json(json_dict, name):
    """
    Raise an error if the JSON object is invalid.

    Args:
        json_dict (Any):
            JSON object to validate.
        name (str):
            Name of the JSON object
    """
    must_be_json_object = f"'{name}' must be a valid JSON object."

    def validate_json(data, path="") -> Union[bool, str]:
        if isinstance(data, dict):
            for k, v in data.items():
                if not isinstance(k, str):
                    location = f"{path}.{k}" if path else k
                    return (
                        f"Invalid type for key '{location}':"
                        f" All keys must be strings, got {type(k).__name__}"
                    )
                result = validate_json(v, f"{path}.{k}" if path else k)
                if result is not True:
                    return result
        elif isinstance(data, list):
            for index, item in enumerate(data):
                result = validate_json(item, f"{path}[{index}]")
                if result is not True:
                    return result
        elif isinstance(data, (int, float, str, bool, type(None))):
            return True
        else:
            return (
                f"Invalid type for value of key '{path}':"
                f" All values must be one of (int, float, str, bool, None, JsonDict, JsonList),"
                f" got {type(data).__name__}"
            )

        return True

    if not isinstance(json_dict, dict):
        raise ValueError(must_be_json_object)

    errors = validate_json(json_dict)
    if isinstance(errors, str):
        raise ValueError(f"Errors in {name}: {errors}")


def get_clean_key(key: str) -> str:
    """
    Removes all special characters from the key.

    Args:
        key (str):
            Key to clean.

    Returns:
        Cleaned key.
    """
    return key.lstrip(f"{SYMBOL_OPTIONAL}{SYMBOL_TYPED}{SYMBOL_DEFAULT}")
