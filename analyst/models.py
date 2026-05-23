from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    type: str
    description: str = ""


class TableSchema(BaseModel):
    catalog: str = "AwsDataCatalog"
    database: str
    table: str
    description: str = ""
    columns: list[ColumnSchema]
    sample_rows: list[dict[str, object]] = Field(default_factory=list)


class SchemaRegisterRequest(BaseModel):
    table_schema: TableSchema


class SchemaRegisterResponse(BaseModel):
    table: str
    column_count: int
    sample_row_count: int


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    catalog: str = "AwsDataCatalog"
    database: str
    max_rows: int = Field(default=100, ge=1, le=1000)


class QueryResponse(BaseModel):
    run_id: str
    question: str
    sql: str
    safe: bool
    safety_notes: list[str]
    explanation: str
    rows: list[dict[str, object]] = Field(default_factory=list)
    row_count: int = 0
    scanned_bytes_estimate: int = 0


class SqlValidation(BaseModel):
    safe: bool
    notes: list[str]


class QueryRunTrace(BaseModel):
    run_id: str
    question: str
    catalog: str
    database: str
    retrieved_tables: list[str]
    sql: str
    validation: SqlValidation
    rows: list[dict[str, object]]
    explanation: str
    latency_ms: float
