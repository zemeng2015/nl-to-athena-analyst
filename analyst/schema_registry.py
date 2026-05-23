import re

from analyst.models import TableSchema


class SchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], TableSchema] = {}

    def register(self, schema: TableSchema) -> None:
        key = (schema.catalog, schema.database, schema.table)
        self._schemas[key] = schema

    def list_tables(self, catalog: str, database: str) -> list[TableSchema]:
        return sorted(
            [
                schema
                for key, schema in self._schemas.items()
                if key[0] == catalog and key[1] == database
            ],
            key=lambda schema: schema.table,
        )

    def retrieve(self, question: str, catalog: str, database: str, limit: int = 3) -> list[TableSchema]:
        terms = tokenize(question)
        scored: list[tuple[int, TableSchema]] = []

        for schema in self.list_tables(catalog, database):
            searchable = " ".join(
                [
                    schema.table,
                    schema.description,
                    *[column.name for column in schema.columns],
                    *[column.description for column in schema.columns],
                ]
            )
            score = len(terms & tokenize(searchable))
            if score > 0:
                scored.append((score, schema))

        return [schema for _, schema in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower())
        if len(token) > 2
    }
