from analyst.models import TableSchema
from analyst.sql_generator import generate_sql


def test_generate_sql_uses_average_for_numeric_column() -> None:
    schema = TableSchema(
        database="analytics",
        table="loan_performance",
        description="Loan performance",
        columns=[
            {"name": "loan_id", "type": "varchar"},
            {"name": "delinquency_rate", "type": "double", "description": "Delinquency rate"},
        ],
    )

    sql = generate_sql("average delinquency rate", [schema], max_rows=50)

    assert sql == "SELECT AVG(delinquency_rate) AS average_delinquency_rate FROM analytics.loan_performance LIMIT 50"


def test_generate_sql_uses_count_when_question_asks_how_many() -> None:
    schema = TableSchema(
        database="analytics",
        table="loans",
        columns=[{"name": "loan_id", "type": "varchar"}],
    )

    sql = generate_sql("how many loans are there?", [schema], max_rows=25)

    assert sql == "SELECT COUNT(*) AS row_count FROM analytics.loans LIMIT 25"
