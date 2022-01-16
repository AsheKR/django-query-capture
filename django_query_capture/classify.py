import typing

import re
from collections import Counter

from django.utils.functional import cached_property

from django_query_capture.capture import CapturedQuery
from django_query_capture.settings import get_config


class DuplicateHashableCapturedQuery(typing.Dict[str, typing.Any]):
    def __hash__(self):
        return hash(self["sql"])

    def __eq__(self, other):
        return self["sql"] == self["sql"]


class SimilarHashableCapturedQuery(typing.Dict[str, typing.Any]):
    def __hash__(self):
        return hash(self["raw_sql"])

    def __eq__(self, other):
        return self["raw_sql"] == self["raw_sql"]


class ClassifiedQuery(typing.TypedDict):
    read: int
    writes: int
    total: int
    total_duration: float
    slow_captured_queries: typing.List[CapturedQuery]
    duplicates_counter: typing.Counter[CapturedQuery]
    duplicates_counter_over_threshold: typing.Counter[CapturedQuery]
    similar_counter: typing.Counter[CapturedQuery]
    similar_counter_over_threshold: typing.Counter[CapturedQuery]
    most_common_duplicate: typing.Optional[typing.Tuple[CapturedQuery, int]]
    most_common_similar: typing.Optional[typing.Tuple[CapturedQuery, int]]
    has_over_threshold: bool
    captured_queries: typing.List[CapturedQuery]


class CapturedQueryClassifier:
    def __init__(
        self,
        captured_queries: typing.List[CapturedQuery],
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        self.ignore_patterns = ignore_patterns or get_config()["IGNORE_SQL_PATTERNS"]
        self.captured_queries = captured_queries
        self.filtered_captured_queries = [
            captured_query
            for captured_query in captured_queries
            if self.is_allow_pattern(captured_query["sql"])
        ]

    def __call__(self) -> ClassifiedQuery:
        return {
            "read": self.read_count,
            "writes": self.writes_count,
            "total": self.total_count,
            "total_duration": self.total_duration,
            "slow_captured_queries": self.slow_captured_queries,
            "duplicates_counter": self.duplicates_counter,
            "duplicates_counter_over_threshold": self.duplicates_counter_over_threshold,
            "similar_counter": self.similar_counter,
            "similar_counter_over_threshold": self.similar_counter_over_threshold,
            "most_common_duplicate": self.most_common_duplicate,
            "most_common_similar": self.most_common_similar,
            "has_over_threshold": self.has_over_threshold,
            "captured_queries": self.captured_queries,
        }

    def is_allow_pattern(self, query: str) -> bool:
        return not list(
            filter(
                lambda pattern: re.compile(pattern).search(query),
                self.ignore_patterns,
            )
        )

    @property
    def read_count(self):
        return sum(
            1
            for capture_query in self.filtered_captured_queries
            if capture_query["raw_sql"].startswith("SELECT")
        )

    @property
    def writes_count(self):
        return sum(
            1
            for capture_query in self.filtered_captured_queries
            if not capture_query["raw_sql"].startswith("SELECT")
        )

    @property
    def total_count(self):
        return len(self.filtered_captured_queries)

    @property
    def total_duration(self) -> float:
        return sum(
            capture_query["duration"]
            for capture_query in self.filtered_captured_queries
        )

    @cached_property
    def slow_captured_queries(self) -> typing.List[CapturedQuery]:
        results = []
        for captured_query in self.filtered_captured_queries:
            if (
                captured_query["duration"]
                > get_config()["PRINT_THRESHOLDS"]["SLOW_MIN_SECOND"]
            ):
                results.append(captured_query)

        return results

    @cached_property
    def duplicates_counter(self) -> typing.Counter[CapturedQuery]:
        counter = Counter()
        for captured_query in self.filtered_captured_queries:
            counter[DuplicateHashableCapturedQuery(captured_query)] += 1

        return counter

    @cached_property
    def duplicates_counter_over_threshold(self) -> typing.Counter[CapturedQuery]:
        counter = Counter()
        for captured_query, count in self.duplicates_counter.items():
            if count > get_config()["PRINT_THRESHOLDS"]["DUPLICATE_MIN_COUNT"]:
                counter[captured_query] = count

        return counter

    @cached_property
    def similar_counter(self) -> typing.Counter[CapturedQuery]:
        counter = Counter()
        for captured_query in self.filtered_captured_queries:
            if (
                self.duplicates_counter[DuplicateHashableCapturedQuery(captured_query)]
                > get_config()["PRINT_THRESHOLDS"]["DUPLICATE_MIN_COUNT"]
            ):
                continue

            counter[SimilarHashableCapturedQuery(captured_query)] += 1

        return counter

    @cached_property
    def similar_counter_over_threshold(self) -> typing.Counter[CapturedQuery]:
        counter = Counter()
        for captured_query, count in self.similar_counter.items():
            if count > get_config()["PRINT_THRESHOLDS"]["SIMILAR_MIN_COUNT"]:
                counter[captured_query] = count

        return counter

    @property
    def most_common_duplicate(
        self,
    ) -> typing.Optional[typing.Tuple[CapturedQuery, int]]:
        try:
            return self.duplicates_counter.most_common(1)[0]
        except IndexError:
            return None

    @property
    def most_common_similar(self) -> typing.Optional[typing.Tuple[CapturedQuery, int]]:
        try:
            return self.similar_counter.most_common(1)[0]
        except IndexError:
            return None

    @property
    def has_over_threshold(self) -> bool:
        if (
            self.similar_counter_over_threshold
            or self.duplicates_counter_over_threshold
            or self.slow_captured_queries
        ):
            return True
        return False
