## The JVAL specification (v0.1)

> Note: This is my first time writing a specification. I'm not sure if I'm doing it right. I'm open to suggestions and corrections.

[1. Inputs](#1-inputs)

[1.1. The schema](#11-the-schema)

[1.1.1. Schema keys](#111-schema-keys)

[1.1.1.1 Special characters](#1111-special-characters)

[1.1.1.1.1 Type validation](#11111-type-validation)

[1.1.1.1.2 Optionality](#11112-optionality)

[1.1.1.1.2.1 Absence of optional keys](#111121-absence-of-optional-keys)

[1.1.1.1.2.2 Presence of unexpected keys](#111122-presence-of-unexpected-keys)

[1.1.1.1.3 Default values for optionals](#11113-default-values-for-optionals)

[1.1.1.1.3.1 Type inference for default values](#111131-type-inference-for-default-values)

[1.1.1.1.4 Type validation for optionals](#11114-type-validation-for-optionals)

[1.1.1.1.5 Literals](#11115-literals)

[1.1.1.2 Key names](#1112-key-names)

[1.1.2 Schema values](#112-schema-values)

[1.1.2.1 Type enclosing characters](#1121-type-enclosing-characters)

[1.1.2.1.1 Valid types](#11211-valid-types)

[1.2. The JSON object to be validated](#12-the-json-object-to-be-validated)

[2. Output](#2-output)

[2.1. Success](#21-success)

[2.2. Failure](#22-failure)

### 1. Inputs

A JVAL validator is a function or routine that takes at least the following two arguments: [1.1. The schema](#11-the-schema) and [1.2. The JSON object to be validated](#12-the-json-object-to-be-validated), and produces an output defined in [2. Output](#2-output).

#### 1.1. The schema

A JSON object representing the schema. This object can be passed as a path to a valid JSON file or as a variable.

Depending on how the programming language represents nested objects, the actual type of this variable may vary. It must be, in any case, an infinitely nestable structure of key-value pairs, where:

#### 1.1.1. Schema keys

Its keys must be strictly strings (sequences of characters) and must be unique within the same object.

#### 1.1.1.1 Special characters

Keys can be annotated by prepending them with one or more special characters, which will be interpreted by the validator.

#### 1.1.1.1.1 Type validation

Define a special character to represent that a key indicates a type requirement for its corresponding value.

#### 1.1.1.1.2 Optionality

Define a special character to represent that a key is optional.

#### 1.1.1.1.2.1 Absence of optional keys

The absence of a nonoptional key in the input object must raise an error by default.

#### 1.1.1.1.2.2 Presence of unexpected keys

The validator should be configurable to ignore the presence of extra keys in the input object that are not defined in the schema.

#### 1.1.1.1.3 Default values for optionals

Define a special character to indicate that the value associated with a key in the schema is a default value. To be interpreted by the validator, this character must be preceded by the character that indicates optionality. Otherwise, it will be assumed to be part of the name of the key.

#### 1.1.1.1.3.1 Type inference for default values

A key defined as optional with a default value in the schema carries the implicit requirement that the type of the value of the corresponding key in the input object, if present, should match the type inferred from the value defined as default in the schema. The validator must perform this type inference and raise an error if the value in the input object does not match the type of the value defined as default in the schema.

#### 1.1.1.1.4 Type validation for optionals

The special character that indicates optionality can be followed by the special character that indicates type requirement to define the type that a value must conform to, if present in the input object. Nonconforming values will be treated as errors.

#### 1.1.1.1.5 Literals

The absence of any special character indicates that the key must be present in the input object with the exact value defined in the schema. If the key is not present or its value is different, an error must be raised.

#### 1.1.1.2 Key names

The string resulting from the removal of all special characters from the beginning of a key defines the expected value for the key in the input object. In this section, the term "name of the key" refers to this string.

#### 1.1.2 Schema values

The supported types are strings, integers, decimal numbers, booleans, lists, other JSON objects, or null.

#### 1.1.2.1 Type enclosing characters

Define special start and end characters to be included in the values of keys that indicate a type requirement. These characters will enclose the specific type required for the value of the key in the input object. If these characters are included in values of keys that do not indicate type requirements, they should be treated as part of the value.

#### 1.1.2.1.1 Valid types

The string enclosed by these characters must be one of the following: "str", "int", "float", or "bool". Any other value will be treated as an error. This error is a JSON schema error and must be identifiable as such and visually distinct from errors that arise from invalid values in the input object.

#### 1.2. The JSON object to be validated

A JSON object representing the input object to validate. This object can be passed as a path to a valid JSON file or as a variable.

Depending on how the programming language represents nested objects, the actual type of this variable may vary. It must be, in any case, an infinitely nestable structure of key-value pairs, where:

Keys must match the same restrictions defined in [1.2 Schema keys](#111-schema-keys) and values must match the same restrictions defined in [1.2 Schema values](#112-schema-values).

### 2. Output

The output for the JVAL validator is a JSON object that represents the result of the validation.

#### 2.1. Success

If the input object complies with the schema, the output must be a JSON object that contains:

- The same keys and values present in the input object.
- Additional keys that are defined in the schema as optional and that are not present in the input object, with the values defined as default in the schema assigned to them.

#### 2.2. Failure

If the input object does not compile with the schema:

- An error indicating the exact location of the problem must be raised or returned.
- The error must contain a location string that points to the exact location of the problem in the input object.
    - The location string must contain the names of the keys that lead to the error, separated by dots to indicate traversing nested JSON objects, and square brackets to indicate the index of the faulty element in a list. For example: "key1.key2[0].key3".
- If the problem is related to a mismatch in the type of a value, the error must contain the expected type and the actual type of the value.
- If the problem is related to the absence of a key that is not optional, the error must contain the name of the missing key.
- If the problem is related to the presence of an unexpected key, the error must contain the name of the unexpected key.
- Errors in the schema must be identified as such and visually distinct from errors that arise from invalid values in the input object.
