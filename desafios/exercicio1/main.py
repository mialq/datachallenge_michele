"""Exemplo executável do módulo de Data Quality."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from .event_validator import handler
except ImportError:  # Permite executar este arquivo diretamente.
    from event_validator import handler


SCHEMA_PATH = Path(__file__).with_name("schema.json")


def load_schema() -> dict:
    """Carrega o schema independentemente do diretório atual do terminal."""
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    schema = load_schema()

    valid_event = {
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

    invalid_event = {
        **valid_event,
        "extraField": "unexpected",
    }

    print("\n1) Evento válido")
    handler(valid_event, schema)

    print("\n2) Evento inválido")
    handler(invalid_event, schema)


if __name__ == "__main__":
    main()
