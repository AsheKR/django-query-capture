import typing

import re
from collections import Counter

from django.utils.functional import cached_property

from django_query_capture.capture import CapturedQuery
from django_query_capture.classify import ClassifiedQuery
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


class BasePresenter:
    def __init__(
        self, classified_query: ClassifiedQuery, include_ignore_patterns: bool = False
    ):
        self._classified_query = classified_query
        self.include_ignore_patterns = include_ignore_patterns

    def print(self) -> None:
        raise NotImplementedError

    @staticmethod
    def is_allow_pattern(query: str) -> bool:
        return not list(
            filter(
                lambda pattern: re.compile(pattern).search(query),
                get_config()["IGNORE_SQL_PATTERNS"],
            )
        )

    @property
    def read_count(self) -> int:
        return self._classified_query["read"]

    @property
    def write_count(self) -> int:
        return self._classified_query["writes"]

    @property
    def total(self) -> int:
        return self._classified_query["total"]

    @property
    def total_duration(self) -> float:
        return self._classified_query["total_duration"]

    @cached_property
    def duplicates_counter(self) -> typing.Counter[CapturedQuery]:
        counter = Counter()
        for captured_query in self._classified_query["captured_queries"]:
            if not self.include_ignore_patterns and not self.is_allow_pattern(
                captured_query["sql"]
            ):
                continue
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
        for captured_query in self._classified_query["captured_queries"]:
            if not self.include_ignore_patterns and not self.is_allow_pattern(
                captured_query["sql"]
            ):
                continue

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
    def captured_queries(self):
        return self._classified_query["captured_queries"]
