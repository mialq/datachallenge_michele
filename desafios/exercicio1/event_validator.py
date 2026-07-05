"""Validação recursiva de eventos com base em um JSON Schema simplificado."""

from __future__ import annotations

import json
from typing import Any


JSON_TYPE_TO_PYTHON_TYPE: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}


def send_event_to_queue(event: dict[str, Any], queue_name: str) -> None:
    """Simula o envio de um evento válido para uma fila."""
    payload = json.dumps(event, ensure_ascii=False)
    print(f"Evento válido. Enviado para a fila {queue_name}: {payload}")


def json_type_to_python_type(json_type: str):
    """Retorna o tipo Python equivalente a um tipo declarado no JSON Schema."""
    return JSON_TYPE_TO_PYTHON_TYPE.get(json_type)


def _matches_type(value: Any, json_type: str) -> bool:
    """Valida tipos evitando que booleanos sejam aceitos como inteiros em Python."""
    expected_type = json_type_to_python_type(json_type)
    if expected_type is None:
        return False

    if json_type in {"integer", "number"} and isinstance(value, bool):
        return False

    return isinstance(value, expected_type)


def validate_event(
    event: Any,
    schema: dict[str, Any],
    path: str = "$",
) -> tuple[bool, str]:
    """Valida obrigatoriedade, tipos, objetos aninhados e campos extras.

    A função implementa apenas o subconjunto de JSON Schema necessário para o
    desafio. Não pretende substituir bibliotecas completas de validação.
    """
    schema_type = schema.get("type", "object")

    if schema_type == "object":
        if not isinstance(event, dict):
            return False, f"Tipo incorreto em '{path}'. Esperado: object"

        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        for field in required_fields:
            if field not in event:
                return False, f"Falta o campo obrigatório: {path}.{field}"

        extra_fields = [field for field in event if field not in properties]
        if extra_fields:
            fields = ", ".join(sorted(extra_fields))
            return False, f"Campo(s) não esperado(s) em '{path}': {fields}"

        for field, value in event.items():
            field_schema = properties[field]
            field_path = f"{path}.{field}"
            is_valid, message = validate_event(value, field_schema, field_path)
            if not is_valid:
                return False, message

        return True, "Evento válido"

    if schema_type == "null":
        return (True, "Evento válido") if event is None else (
            False,
            f"Tipo incorreto em '{path}'. Esperado: null, encontrado: {type(event).__name__}",
        )

    if json_type_to_python_type(schema_type) is None:
        return False, f"Tipo de schema não suportado em '{path}': {schema_type}"

    if not _matches_type(event, schema_type):
        return False, (
            f"Tipo incorreto em '{path}'. Esperado: {schema_type}, "
            f"encontrado: {type(event).__name__}"
        )

    return True, "Evento válido"


def handler(event: dict[str, Any], schema: dict[str, Any]) -> bool:
    """Valida o evento e simula o roteamento apenas quando ele é válido."""
    is_valid, message = validate_event(event, schema)

    if is_valid:
        send_event_to_queue(event, "valid-events-queue")
        return True

    print(f"Evento inválido. Não enviado. Motivo: {message}")
    return False
