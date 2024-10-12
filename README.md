# JVAL - JSON Validation Language - Python Module

JVAL allows for structural and type validation of JSON objects.
This project defines the JVAL specification and presents a sample implementation in Python.

## Features

JVAL...

- is isomorphic to JSON. This means that it takes the same amount of lines to define a schema as it does to define a JSON object that complies with such schema, no matter how complex you decide to make it.
- supports nested type definitions and optional fields with default values.
- produces descriptive error messages that point to the exact location of the problem.
- will, not only notify you of errors in the JSON object but also in the schema itself, helping you write and understand your schemas.
- can be configured to discard extra fields in the JSON object instead of raising an error if they are present. This enables the usage of JVAL for filtering as well as validation.
- takes specs written in JSON, making syntax highlighting, autocompletion, and formatting available in your favorite text editor out of the box.

## A JVAL Schema Example

```js
{
  "version": "1.0",
  // Expect a "version" key with a value of "1.0"

  "*name": "<str>",
  // Expect a "name" key with a value of type string

  "?compression": "7zip",
  // Optional "compression" key. Must have a value of "7zip" if present.

  "?*dependencies": ["<str>"],
  // Optional "dependencies" key. Must be a list of strings if present.

  "?_visibility": "private",
  // Optional "visibility" key. Assume a default value of "private" if not present.
  // Must be a value of type string if present. (Infers type from default value).

  "*addresses": [
    // Type requirements can be as complex or simple as you need them to be.
 {
      "*street": "<str>",
      "*number": "<int>",
      "?*complement": "<str>",
 },
 ],
}
```

A schema like the one above is passed to the validator along with a JSON object to validate.

The function will return the validated data, adding any default values that are missing from the input JSON object.
If the object does not comply with the schema, it will raise an exception that includes the exact location of the error.

## Usage

After installing the package with `pip install jval` you can either use it as a command line tool or import it in your Python code as a module.

### Command-line usage

```bash
usage: jval [-h] [--drop-extra-keys] json_path jval_path

Validate JSON data against a JVAL schema.

Positional arguments:
  json_path          Path to the JSON file to validate
  jval_path          Path to the JVAL schema file

Options:
  -h, --help         Show this help message and exit
  --drop-extra-keys  Drop extra keys in the JSON data that are not defined in the JVAL schema
```

### Python module usage

```python
from jval import validate

schema = {
    "*name": "<str>",
    "?*age": "<int>",
    "?_has_pets": False,
    "?*properties": [
 {
        "*name": "<str>",
        "*address": "<str>"
 }
 ]
}

data = {
    "name": "Alice",
    "properties": [
 {
        "name": "Long Island Apartment",
        "address": "1234 Long Island St."
 }
 ]
}

validated_data = validate(data, schema)
print(validated_data)
```

Output:

```python
{
    "name": "Alice",
    "has_pets": False,
    "properties": [
 {
        "name": "Long Island Apartment",
        "address": "1234 Long Island St."
 }
 ]
}
```
