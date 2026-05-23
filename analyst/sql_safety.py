import sqlglot

from analyst.models import SqlValidation


BLOCKED_KEYWORDS = {"DELETE", "DROP", "INSERT", "UPDATE", "MERGE", "ALTER", "CREATE"}


def validate_sql(sql: str) -> SqlValidation:
    notes: list[str] = []
    upper_sql = sql.upper()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in upper_sql.split():
            notes.append(f"Blocked keyword found: {keyword}")

    if ";" in sql.strip().rstrip(";"):
        notes.append("Multiple SQL statements are not allowed.")

    try:
        parsed = sqlglot.parse_one(sql, read="athena")
    except sqlglot.errors.ParseError as exc:
        notes.append(f"SQL parse failed: {exc}")
        return SqlValidation(safe=False, notes=notes)

    if parsed.key.upper() != "SELECT":
        notes.append("Only SELECT statements are allowed.")

    if "LIMIT" not in upper_sql:
        notes.append("Query must include LIMIT.")

    return SqlValidation(safe=not notes, notes=notes)
