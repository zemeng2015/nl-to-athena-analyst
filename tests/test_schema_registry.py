from analyst.models import TableSchema
from analyst.schema_registry import SchemaRegistry


def test_registry_retrieves_relevant_schema() -> None:
    registry = SchemaRegistry()
    registry.register(
        TableSchema(
            database="analytics",
            table="loan_performance",
            description="Mortgage loan delinquency and borrower risk metrics",
            columns=[
                {"name": "loan_id", "type": "varchar"},
                {"name": "delinquency_rate", "type": "double"},
            ],
        )
    )

    results = registry.retrieve("average delinquency for mortgage loans", "AwsDataCatalog", "analytics")

    assert results[0].table == "loan_performance"
