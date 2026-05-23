# Natural Language to Athena Analyst

Enterprise data assistant that converts natural language questions into governed Athena SQL, executes safe queries, and explains results.

## Why This Project

This project highlights the intersection of AI engineering, data engineering, and enterprise governance. It is a strong fit for your AWS, Athena, S3, backend, and analytics platform background.

## Target Resume Bullet

Built a natural-language analytics assistant that translates business questions into governed Athena SQL with schema retrieval, query safety checks, execution tracing, and result explanation.

## Core Capabilities

- Retrieve relevant schemas and data dictionary entries.
- Generate Athena SQL from natural language.
- Validate SQL before execution.
- Estimate query cost and enforce limits.
- Explain results with charts and caveats.
- Evaluate SQL accuracy against a golden dataset.

## Current Implementation

This first version is a governed, local-first Athena analyst. It does not require
AWS credentials, but it models the production workflow: schema registration,
schema retrieval, SQL generation, SQL safety validation, mock execution, and
run tracing.

- `POST /schemas` registers table schemas, column descriptions, and sample rows.
- `GET /schemas` lists registered schemas by catalog and database.
- `POST /query` retrieves relevant schemas, generates Athena SQL, validates it,
  executes against a local Athena mock, and explains the result.
- `GET /runs/{run_id}` returns the generated SQL, retrieved tables, validation
  notes, rows, and latency.
- SQL safety blocks DDL/DML, multiple statements, non-SELECT queries, and queries
  without `LIMIT`.
- Tests cover safety validation, schema retrieval, SQL generation, mock Athena
  execution, and API traces.

## Suggested Stack

- Backend: FastAPI, Pydantic
- SQL parsing: sqlglot
- AWS: Athena, Glue Catalog, S3
- AI: OpenAI API or AWS Bedrock
- Evaluation: exact SQL checks plus result-set comparison

## Milestones

1. Build schema registry and retrieval.
2. Add SQL generation prompt and safety validation.
3. Add Athena adapter interface with local mock.
4. Add result explanation.
5. Add SQL accuracy eval suite.

## Local Development

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn analyst.main:app --reload
python -m pytest
python -m ruff check .
```

## API Example

Register a sample schema:

```powershell
$body = Get-Content .\samples\loan_performance_schema.json -Raw

Invoke-RestMethod -Uri http://127.0.0.1:8000/schemas `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Ask an analytics question:

```powershell
$body = @{
  database = "analytics"
  question = "What is the average delinquency rate?"
  max_rows = 100
} | ConvertTo-Json -Depth 5

$result = Invoke-RestMethod -Uri http://127.0.0.1:8000/query `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

$result
```

Inspect the run trace:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runs/$($result.run_id)"
```

## Next Milestones

1. Add OpenAI or Bedrock SQL generation with schema-grounded prompts.
2. Add stricter governance: table allowlists, column masking, and cost limits.
3. Add real Athena adapter using `boto3`.
4. Add result-set comparison evals.
5. Add CI quality gates for SQL safety and golden query accuracy.
