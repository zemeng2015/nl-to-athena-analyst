from analyst.models import TableSchema
from analyst.schema_registry import tokenize


AGGREGATION_TERMS = {"average", "avg", "mean"}
COUNT_TERMS = {"count", "number", "many"}


def generate_sql(question: str, schemas: list[TableSchema], max_rows: int = 100) -> str:
    if not schemas:
        return f"SELECT 'No matching schema found' AS message LIMIT {max_rows}"

    schema = schemas[0]
    terms = tokenize(question)
    table_ref = f"{schema.database}.{schema.table}"

    numeric_columns = [
        column.name
        for column in schema.columns
        if column.type.lower() in {"int", "integer", "bigint", "double", "float", "decimal"}
    ]
    matching_columns = [
        column.name
        for column in schema.columns
        if column.name.lower() in terms or terms & tokenize(column.description)
    ]

    if terms & COUNT_TERMS:
        return f"SELECT COUNT(*) AS row_count FROM {table_ref} LIMIT {max_rows}"

    if terms & AGGREGATION_TERMS and numeric_columns:
        column = first_matching(matching_columns, numeric_columns) or numeric_columns[0]
        return f"SELECT AVG({column}) AS average_{column} FROM {table_ref} LIMIT {max_rows}"

    selected_columns = matching_columns[:5] or [column.name for column in schema.columns[:5]]
    return f"SELECT {', '.join(selected_columns)} FROM {table_ref} LIMIT {max_rows}"


def first_matching(candidates: list[str], allowed: list[str]) -> str | None:
    allowed_set = set(allowed)
    for candidate in candidates:
        if candidate in allowed_set:
            return candidate
    return None
