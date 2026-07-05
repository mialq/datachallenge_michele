"""Testes unitários do validador de eventos."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from desafios.exercicio1.event_validator import (
    json_type_to_python_type,
    validate_event,
)


SCHEMA_PATH = Path(__file__).with_name("schema.json")


class TestJsonTypeToPythonType(unittest.TestCase):
    def test_conversion(self) -> None:
        self.assertEqual(json_type_to_python_type("string"), str)
        self.assertEqual(json_type_to_python_type("integer"), int)
        self.assertEqual(json_type_to_python_type("boolean"), bool)
        self.assertEqual(json_type_to_python_type("object"), dict)
        self.assertIsNone(json_type_to_python_type("unknown"))


class TestValidateEvent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with SCHEMA_PATH.open("r", encoding="utf-8") as file:
            cls.schema = json.load(file)

        cls.valid_event = {
            "eid": "12345",
            "documentNumber": "67890",
            "name": "Renata",
            "age": 30,
            "address": {
                "street": "Rua da Alegria",
                "number": 100,
                "mailAddress": True,
            },
        }

    def test_valid_event(self) -> None:
        is_valid, message = validate_event(self.valid_event, self.schema)
        self.assertTrue(is_valid, message)

    def test_missing_required_nested_field(self) -> None:
        event = {**self.valid_event, "address": {"street": "Rua A", "mailAddress": True}}
        is_valid, message = validate_event(event, self.schema)
        self.assertFalse(is_valid)
        self.assertIn("number", message)

    def test_rejects_extra_field(self) -> None:
        event = {**self.valid_event, "extraField": "unexpected"}
        is_valid, message = validate_event(event, self.schema)
        self.assertFalse(is_valid)
        self.assertIn("extraField", message)

    def test_rejects_wrong_nested_type(self) -> None:
        event = {
            **self.valid_event,
            "address": {**self.valid_event["address"], "mailAddress": "yes"},
        }
        is_valid, message = validate_event(event, self.schema)
        self.assertFalse(is_valid)
        self.assertIn("mailAddress", message)

    def test_boolean_is_not_accepted_as_integer(self) -> None:
        event = {**self.valid_event, "age": True}
        is_valid, message = validate_event(event, self.schema)
        self.assertFalse(is_valid)
        self.assertIn("age", message)


if __name__ == "__main__":
    unittest.main()
