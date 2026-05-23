from analyst.sql_safety import validate_sql


def test_validate_sql_allows_limited_select() -> None:
    result = validate_sql("SELECT * FROM loans LIMIT 10")
    assert result.safe


def test_validate_sql_blocks_drop() -> None:
    result = validate_sql("DROP TABLE loans")
    assert not result.safe


def test_validate_sql_blocks_multiple_statements() -> None:
    result = validate_sql("SELECT * FROM loans LIMIT 10; DROP TABLE loans")
    assert not result.safe


def test_validate_sql_requires_limit() -> None:
    result = validate_sql("SELECT * FROM loans")
    assert not result.safe
