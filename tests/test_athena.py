from analyst.athena import LocalAthenaMock
from analyst.models import TableSchema


def test_local_athena_mock_executes_average() -> None:
    schema = TableSchema(
        database="analytics",
        table="loan_performance",
        columns=[{"name": "delinquency_rate", "type": "double"}],
        sample_rows=[
            {"delinquency_rate": 0.02},
            {"delinquency_rate": 0.04},
        ],
    )

    rows, scanned_bytes = LocalAthenaMock().execute(
        "SELECT AVG(delinquency_rate) AS average_delinquency_rate "
        "FROM analytics.loan_performance LIMIT 100",
        [schema],
    )

    assert rows == [{"average_delinquency_rate": 0.03}]
    assert scanned_bytes > 0
