"""Conversão de um JSON Schema simplificado em DDL para Amazon Athena."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(identifier: str) -> str:
    """Aceita somente identificadores simples para tabela e colunas."""
    if not _IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"Identificador inválido: {identifier!r}")
    return identifier


def json_schema_to_athena_type(field_schema: dict[str, Any]) -> str:
    """Mapeia tipos do JSON Schema para tipos compatíveis com DDL do Athena."""
    json_type = field_schema.get("type")

    primitive_mapping = {
        "string": "STRING",
        "integer": "INT",
        "number": "DOUBLE",
        "boolean": "BOOLEAN",
    }

    if json_type in primitive_mapping:
        return primitive_mapping[json_type]

    if json_type == "object":
        nested_fields = []
        for field_name, nested_schema in field_schema.get("properties", {}).items():
            _validate_identifier(field_name)
            nested_type = json_schema_to_athena_type(nested_schema)
            nested_fields.append(f"{field_name}:{nested_type}")
        return f"STRUCT<{','.join(nested_fields)}>"

    if json_type == "array":
        item_schema = field_schema.get("items")
        if not isinstance(item_schema, dict):
            raise ValueError("Campos do tipo array devem declarar 'items'.")
        return f"ARRAY<{json_schema_to_athena_type(item_schema)}>"

    raise ValueError(f"Tipo JSON Schema não suportado: {json_type!r}")


def schema_to_athena_ddl(
    schema: dict[str, Any],
    table_name: str = "data_quality_module",
    s3_location: str = "s3://your-data-bucket/path/to/data/",
) -> str:
    """Gera uma DDL de tabela externa particionada e armazenada em Parquet."""
    _validate_identifier(table_name)

    if not s3_location.startswith("s3://"):
        raise ValueError("s3_location deve começar com 's3://'.")
    if not s3_location.endswith("/"):
        s3_location += "/"

    ddl_columns = []
    for field_name, field_schema in schema.get("properties", {}).items():
        _validate_identifier(field_name)
        athena_type = json_schema_to_athena_type(field_schema)
        ddl_columns.append(f"  {field_name} {athena_type}")

    columns_sql = ",\n".join(ddl_columns)

    return (
        f"CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (\n"
        f"{columns_sql}\n"
        ")\n"
        "PARTITIONED BY (\n"
        "  year INT,\n"
        "  month INT,\n"
        "  day INT\n"
        ")\n"
        "STORED AS PARQUET\n"
        f"LOCATION '{s3_location}';"
    )


def create_table_with_athena(query: str) -> None:
    """Simula a execução da DDL; não realiza chamada real à AWS."""
    print("DDL gerada para Amazon Athena:\n")
    print(query)


def handler(schema_path: Path | None = None) -> str:
    """Carrega o schema, gera a DDL e executa a simulação."""
    schema_path = schema_path or Path(__file__).with_name("schema.json")

    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    query = schema_to_athena_ddl(schema)
    create_table_with_athena(query)
    return query
