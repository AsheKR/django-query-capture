import typing

from django_query_capture.capture import CapturedQuery


class ClassifiedQuery(typing.TypedDict):
    read: int
    writes: int
    total: int
    total_duration: float
    captured_queries: typing.List[CapturedQuery]


class CapturedQueryClassifier:
    def __init__(self, captured_queries: typing.List[CapturedQuery]):
        self.captured_queries = captured_queries

    def __call__(self) -> ClassifiedQuery:
        stats: ClassifiedQuery = {
            "read": self.get_read_count(),
            "writes": self.get_writes_count(),
            "total": self.get_total_count(),
            "total_duration": self.get_total_duration(),
            "captured_queries": self.captured_queries,
        }

        return stats

    def get_read_count(self):
        return sum(
            1
            for capture_query in self.captured_queries
            if capture_query["raw_sql"].startswith("SELECT")
        )

    def get_writes_count(self):
        return sum(
            1
            for capture_query in self.captured_queries
            if not capture_query["raw_sql"].startswith("SELECT")
        )

    def get_total_count(self):
        return len(self.captured_queries)

    def get_total_duration(self) -> float:
        return sum(capture_query["duration"] for capture_query in self.captured_queries)
