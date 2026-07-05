"""Testes unitários do gerador de DDL para Athena."""

from __future__ import annotations

import unittest

from desafios.exercicio2.json_schema_to_athena import (
    json_schema_to_athena_type,
    schema_to_athena_ddl,
)


class TestAthenaDDL(unittest.TestCase):
    def test_nested_object_becomes_struct(self) -> None:
        field_schema = {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "number": {"type": "integer"},
            },
        }
        self.assertEqual(
            json_schema_to_athena_type(field_schema),
            "STRUCT<street:STRING,number:INT>",
        )

    def test_ddl_contains_partition_and_parquet(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "eid": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        ddl = schema_to_athena_ddl(schema, s3_location="s3://bucket/data")
        self.assertIn("eid STRING", ddl)
        self.assertIn("PARTITIONED BY", ddl)
        self.assertIn("STORED AS PARQUET", ddl)
        self.assertIn("LOCATION 's3://bucket/data/'", ddl)

    def test_invalid_table_identifier_is_rejected(self) -> None:
        schema = {"type": "object", "properties": {}}
        with self.assertRaises(ValueError):
            schema_to_athena_ddl(schema, table_name="bad-name")


if __name__ == "__main__":
    unittest.main()
