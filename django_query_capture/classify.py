import typing

from collections import Counter

from django_query_capture.capture import CapturedQuery


class ClassifiedQuery(typing.TypedDict):
    read: int
    writes: int
    total: int
    total_duration: float
    most_common_duplicates: int
    most_common_similar: int
    duplicates_counter: typing.Counter[str]
    similar_counter: typing.Counter[str]
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
            "most_common_duplicates": 0,
            "most_common_similar": 0,
            "duplicates_counter": self.get_duplicates_counter(),
            "similar_counter": self.get_similar_counter(),
            "captured_queries": self.captured_queries,
        }
        most_common_duplicates = stats["duplicates_counter"].most_common(1)
        if most_common_duplicates:
            sql, count = most_common_duplicates[0]
            stats["most_common_duplicates"] = count

        most_common_similar = stats["similar_counter"].most_common(1)
        if most_common_similar:
            sql, count = most_common_similar[0]
            stats["most_common_similar"] = count

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

    def get_duplicates_counter(self) -> typing.Counter[str]:
        duplicates_counter: typing.Counter[str] = Counter()
        for capture_query in self.captured_queries:
            if capture_query["sql"]:
                duplicates_counter[capture_query["sql"]] += 1

        return duplicates_counter

    def get_similar_counter(self) -> typing.Counter[str]:
        similar_counter: typing.Counter[str] = Counter()
        for capture_query in self.captured_queries:
            if capture_query["raw_sql"]:
                similar_counter[capture_query["raw_sql"]] += 1

        return similar_counter
