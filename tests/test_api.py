from fastapi.testclient import TestClient

from analyst.main import app


def test_register_schema_query_and_fetch_trace() -> None:
    client = TestClient(app)

    schema_response = client.post(
        "/schemas",
        json={
            "table_schema": {
                "database": "analytics",
                "table": "loan_performance",
                "description": "Mortgage delinquency and borrower risk metrics",
                "columns": [
                    {"name": "loan_id", "type": "varchar"},
                    {
                        "name": "delinquency_rate",
                        "type": "double",
                        "description": "Loan delinquency rate",
                    },
                ],
                "sample_rows": [
                    {"loan_id": "loan-1", "delinquency_rate": 0.02},
                    {"loan_id": "loan-2", "delinquency_rate": 0.04},
                ],
            }
        },
    )

    assert schema_response.status_code == 200

    query_response = client.post(
        "/query",
        json={
            "database": "analytics",
            "question": "What is the average delinquency rate?",
            "max_rows": 100,
        },
    )
    body = query_response.json()

    assert query_response.status_code == 200
    assert body["safe"]
    assert body["rows"] == [{"average_delinquency_rate": 0.03}]
    assert body["run_id"]

    trace_response = client.get(f"/runs/{body['run_id']}")
    trace_body = trace_response.json()

    assert trace_response.status_code == 200
    assert trace_body["retrieved_tables"] == ["loan_performance"]
    assert trace_body["latency_ms"] >= 0
