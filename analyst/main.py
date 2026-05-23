import time
import uuid

from fastapi import FastAPI
from fastapi import HTTPException

from analyst.athena import LocalAthenaMock
from analyst.models import (
    QueryRequest,
    QueryResponse,
    QueryRunTrace,
    SchemaRegisterRequest,
    SchemaRegisterResponse,
    TableSchema,
)
from analyst.schema_registry import SchemaRegistry
from analyst.sql_generator import generate_sql
from analyst.sql_safety import validate_sql
from analyst.tracing import InMemoryRunStore

app = FastAPI(title="Natural Language to Athena Analyst")
registry = SchemaRegistry()
athena = LocalAthenaMock()
run_store = InMemoryRunStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/schemas", response_model=SchemaRegisterResponse)
def register_schema(request: SchemaRegisterRequest) -> SchemaRegisterResponse:
    registry.register(request.table_schema)
    return SchemaRegisterResponse(
        table=request.table_schema.table,
        column_count=len(request.table_schema.columns),
        sample_row_count=len(request.table_schema.sample_rows),
    )


@app.get("/schemas", response_model=list[TableSchema])
def list_schemas(catalog: str = "AwsDataCatalog", database: str = "") -> list[TableSchema]:
    return registry.list_tables(catalog, database)


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    run_id = str(uuid.uuid4())
    start = time.perf_counter()
    retrieved_schemas = registry.retrieve(request.question, request.catalog, request.database)
    sql = generate_sql(request.question, retrieved_schemas, request.max_rows)
    validation = validate_sql(sql)
    rows: list[dict[str, object]] = []
    scanned_bytes_estimate = 0

    if validation.safe:
        rows, scanned_bytes_estimate = athena.execute(sql, retrieved_schemas)

    explanation = explain_result(request.question, sql, rows, validation.notes)
    trace = QueryRunTrace(
        run_id=run_id,
        question=request.question,
        catalog=request.catalog,
        database=request.database,
        retrieved_tables=[schema.table for schema in retrieved_schemas],
        sql=sql,
        validation=validation,
        rows=rows,
        explanation=explanation,
        latency_ms=(time.perf_counter() - start) * 1000,
    )
    run_store.save(trace)
    return QueryResponse(
        run_id=run_id,
        question=request.question,
        sql=sql,
        safe=validation.safe,
        safety_notes=validation.notes,
        explanation=explanation,
        rows=rows,
        row_count=len(rows),
        scanned_bytes_estimate=scanned_bytes_estimate,
    )


@app.get("/runs/{run_id}", response_model=QueryRunTrace)
def get_run(run_id: str) -> QueryRunTrace:
    trace = run_store.get(run_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return trace


def explain_result(
    question: str,
    sql: str,
    rows: list[dict[str, object]],
    safety_notes: list[str],
) -> str:
    if safety_notes:
        return "Query was not executed because it failed safety validation."
    if not rows:
        return f"No rows were returned for: {question}"
    return f"Generated governed Athena SQL and returned {len(rows)} row(s): {sql}"
