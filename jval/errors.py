"""
This module contains the error handling functions for the jval package.
"""

def raise_error(key, message, context):
    """
    Raise a validation error.

    Args:
        key (str):
            Key that caused the validation error.
        message (str):
            Error message.
        context (str):
            Context of the validation error.
    """
    return_str = ""
    if context.strip():
        return_str += f"Validation error at '{context}': "
    else:
        return_str += "Validation error at root: "
    return_str += f"{message} for key '{key}'"
    raise ValueError(return_str)
