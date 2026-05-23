from analyst.models import QueryRunTrace


class InMemoryRunStore:
    def __init__(self) -> None:
        self._runs: dict[str, QueryRunTrace] = {}

    def save(self, trace: QueryRunTrace) -> None:
        self._runs[trace.run_id] = trace

    def get(self, run_id: str) -> QueryRunTrace | None:
        return self._runs.get(run_id)
