import re

from analyst.models import TableSchema


class LocalAthenaMock:
    def execute(self, sql: str, schemas: list[TableSchema]) -> tuple[list[dict[str, object]], int]:
        schema = find_schema_for_sql(sql, schemas)
        if schema is None:
            return [], 0

        rows = schema.sample_rows
        scanned_bytes = sum(len(str(row)) for row in rows)
        upper_sql = sql.upper()

        if "COUNT(*)" in upper_sql:
            return [{"row_count": len(rows)}], scanned_bytes

        avg_match = re.search(r"AVG\((?P<column>[A-Za-z_][A-Za-z0-9_]*)\)", sql, re.IGNORECASE)
        if avg_match:
            column = avg_match.group("column")
            values = [row[column] for row in rows if isinstance(row.get(column), (int, float))]
            average = sum(values) / len(values) if values else 0
            return [{f"average_{column}": average}], scanned_bytes

        selected_columns = parse_selected_columns(sql)
        if selected_columns == ["*"]:
            return rows, scanned_bytes
        return [
            {column: row.get(column) for column in selected_columns if column in row}
            for row in rows
        ], scanned_bytes


def find_schema_for_sql(sql: str, schemas: list[TableSchema]) -> TableSchema | None:
    for schema in schemas:
        if f"{schema.database}.{schema.table}".lower() in sql.lower():
            return schema
    return schemas[0] if schemas else None


def parse_selected_columns(sql: str) -> list[str]:
    match = re.search(r"SELECT\s+(?P<columns>.*?)\s+FROM\s", sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return ["*"]
    raw_columns = match.group("columns").strip()
    if raw_columns == "*":
        return ["*"]
    return [
        column.strip().split()[-1]
        for column in raw_columns.split(",")
        if "(" not in column
    ]
