"""
JVAL - JSON Validation Library
"""

import argparse
import json
import sys
import urllib.parse
from typing import Any, Dict, List, Union
import traceback

from .validation import _validate, raise_if_invalid_json

JsonDict = Dict[str, Union[int, float, str, bool, None, "JsonDict", "JsonList"]]
JsonList = List[Union[int, float, str, bool, None, "JsonDict", "JsonList"]]


def validate(
    json_dict: JsonDict,
    jval_schema: JsonDict,
    *,
    drop_extra_keys: bool = False,
) -> Any:
    """
    Validate JSON data against a JVAL schema.

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
    try:
        return _validate(
            json_dict,
            jval_schema,
            drop_extra_keys=drop_extra_keys,
        )

    except Exception as exc:

        # If e was a value error and starts with validation error, raise it
        if exc.__class__ == ValueError and str(exc).startswith("Validation error"):
            raise ValueError(str(exc)) from None

        # If any of the JSON objects are invalid, raise an error
        try:
            raise_if_invalid_json(json_dict, "json_dict")
            raise_if_invalid_json(jval_schema, "jval_schema")
        except Exception as json_exc:
            raise ValueError(str(json_exc)) from None

        # The error is unexpected, but we can still provide a link to submit the issue
        title = "Unexpected crash in JVAL validator"
        title = urllib.parse.quote(title)

        body = (
            f"**Traceback:**\n{traceback.format_exc()}\n\n"
            "-- If possible, please include the JSON data and JVAL schema here. --\n"
        )

        body = urllib.parse.quote(body)

        text = (
            f"{traceback.format_exc()}\n\n"
            "Oh no! The validator crashed unexpectedly!\n"
            "Please click the following link to submit the issue:\n"
            f"https://github.com/julynx/jval/issues/new?title={title}&body={body}"
        )

        raise ValueError(text) from None


def main():
    """
    Command-line interface for the JVAL validator.
    """
    parser = argparse.ArgumentParser(
        description="Validate JSON data against a JVAL schema."
    )
    parser.add_argument(
        "json_path",
        type=argparse.FileType("r"),
        help="Path to the JSON file to validate",
    )
    parser.add_argument(
        "jval_path",
        type=argparse.FileType("r"),
        help="Path to the JVAL schema file",
    )
    parser.add_argument(
        "--drop-extra-keys",
        action="store_true",
        help="Drop extra keys in the JSON data that are not defined in the JVAL schema",
    )
    args = parser.parse_args()

    try:
        json_data = json.load(args.json_file)
        jval_schema = json.load(args.jval_file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        validated_data = validate(
            json_data, jval_schema, drop_extra_keys=args.drop_extra_keys
        )
        print(json.dumps(validated_data, indent=2))
        sys.exit(0)
    # pylint: disable=broad-except
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
