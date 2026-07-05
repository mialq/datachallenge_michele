"""Ponto de entrada do exercício de geração de DDL para Athena."""

try:
    from .json_schema_to_athena import handler
except ImportError:  # Permite executar este arquivo diretamente.
    from json_schema_to_athena import handler


if __name__ == "__main__":
    handler()
