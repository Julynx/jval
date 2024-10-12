"""
Test cases for JSON Validation using JVAL schema.
"""

import json
import unittest
from pathlib import Path
from typing import Any, Dict, Union
from jval import validate


def read_test_cases(test_folder):
    """
    Read test cases from JSON files in the given folder.

    Args:
        test_folder (str): Path to the folder containing test cases.

    Returns:
        list: List of dictionaries containing test case details.
    """
    # Function to read test cases from JSON files
    test_cases = []
    test_folder = Path(test_folder)

    for test_dir in test_folder.iterdir():
        if test_dir.is_dir():
            test_name = test_dir.name

            json_file_path = test_dir / f"{test_name}.json"
            jval_file_path = test_dir / f"{test_name}.jval.json"
            out_file_path = test_dir / f"{test_name}.out"
            kwargs_file_path = test_dir / "kwargs.json"

            with json_file_path.open("r") as json_file:
                input_json = json.load(json_file)

            with jval_file_path.open("r") as jval_file:
                input_schema = json.load(jval_file)

            with out_file_path.open("r") as out_file:
                content = out_file.read().strip()
                if not content:
                    print(f"El archivo {out_file_path} está vacío o no se puede leer.")
                try:
                    expected_output = json.loads(content)
                except json.JSONDecodeError:
                    expected_output = content

            kwargs = {}
            if kwargs_file_path.exists():
                with kwargs_file_path.open("r") as kwargs_file:
                    kwargs = json.load(kwargs_file)

            test_dict = {
                "name": test_name,
                "input_json": input_json,
                "jval_schema": input_schema,
                "expected_output": expected_output,
            }
            if kwargs:
                test_dict.update(kwargs)
            test_cases.append(test_dict)

    return test_cases


class TestJSONValidation(unittest.TestCase):
    """
    Test class for JSON Validation using JVAL schema.
    """

    test_cases = read_test_cases("tests")  # Load test cases as a class attribute

    def run_test(
        self,
        name: str,
        input_json: str,
        jval_schema: Dict[str, Any],
        expected_output: Union[Dict[str, Any], str],
        **kwargs: Any,
    ) -> None:
        """
        Run a test to validate JSON against JVAL schema and
        check the expected output or error.
        """
        try:
            validated_output = validate(input_json, jval_schema, **kwargs)
            if isinstance(expected_output, dict):
                self.assertEqual(
                    validated_output,
                    expected_output,
                    (
                        f"Test '{name}' Failed: Output mismatch.\n"
                        f"Expected: {expected_output}\nGot: {validated_output}"
                    ),
                )
            else:
                self.fail(
                    f"Test '{name}' Failed: Expected validation error"
                    f" but got valid output: {validated_output}"
                )
        except ValueError as e:
            if isinstance(expected_output, str):
                self.assertEqual(
                    str(e),
                    expected_output,
                    f"Test '{name}' Failed: Error message mismatch.\n"
                    f"Expected: {expected_output}\nGot: {e}",
                )
            else:
                self.fail(
                    f"Test '{name}' Failed: Unexpected validation error: {e}\n"
                    f"Expected: {expected_output}"
                )

    @classmethod
    def create_test_method(cls, case):
        """Dynamically create a test method for each case."""

        def test_method(self):
            self.run_test(**case)

        test_method.__name__ = f"test_{case['name']}"  # Set the test method name
        return test_method

    @classmethod
    def generate_tests(cls):
        """Generate tests dynamically."""
        for case in cls.test_cases:
            test_method = cls.create_test_method(case)
            setattr(cls, test_method.__name__, test_method)


# Generate tests
TestJSONValidation.generate_tests()

if __name__ == "__main__":
    unittest.main()
