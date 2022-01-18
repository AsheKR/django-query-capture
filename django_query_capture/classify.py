"""
If [native_query_capture][capture.native_query_capture] has received data, it serves to refine the data into the necessary data.

???+ warning "HashableCapturedQuery"
    In order to use `collection.Counter`, it was necessary to change the dict form to a hashable dict form.<br>
    So, to classify `Duplicate` and `Similar`, we convert [CapturedQuery][capture.CapturedQuery] dict into HashableDict form and use it as Counter's key.<br>
    If there is a better way, feel free to leave it as an issue or PR.
"""

import typing

import re
from collections import Counter
from functools import cached_property

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
    """
    This is the result of Classifier refining list of [CapturedQuery][capture.CapturedQuery].
    You can freely make output this data from the `Presenter`.
    """

    read: int
    writes: int
    total: int
    total_duration: float
    slow_captured_queries: typing.List[CapturedQuery]
    duplicates_counter: typing.Counter[CapturedQuery]
    duplicates_counter_over_threshold: typing.Counter[CapturedQuery]
    similar_counter: typing.Counter[CapturedQuery]
    similar_counter_over_threshold: typing.Counter[CapturedQuery]
    most_common_duplicate: typing.Union[
        typing.Tuple[CapturedQuery, int], typing.Tuple[None, None]
    ]
    most_common_similar: typing.Union[
        typing.Tuple[CapturedQuery, int], typing.Tuple[None, None]
    ]
    has_over_threshold: bool
    captured_queries: typing.List[CapturedQuery]


class CapturedQueryClassifier:
    """
    This is the result of Classifier refining list of [CapturedQuery][capture.CapturedQuery].
    You can freely make output this data from the `Presenter`.
    """

    def __init__(
        self,
        captured_queries: typing.List[CapturedQuery],
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        """
        Args:
            captured_queries: A list of [CapturedQuery][capture.CapturedQuery] collected by [native_query_capture][capture.native_query_capture].
            ignore_patterns: REGEX string list that will not be used for classification among [CapturedQuery][capture.CapturedQuery].
        """
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
        """
        Args:
            query: It's simply a sql string.

        Returns:
            It is a list of [CapturedQuery][capture.CapturedQuery] that is not caught in ignore_patterns, that is, a classification target.
        """
        return not list(
            filter(
                lambda pattern: re.compile(pattern).search(query),
                self.ignore_patterns,
            )
        )

    @property
    def read_count(self) -> int:
        """
        Returns:
            number of `SELECT` statement
        """
        return sum(
            1
            for capture_query in self.filtered_captured_queries
            if capture_query["raw_sql"].startswith("SELECT")
        )

    @property
    def writes_count(self) -> int:
        """
        Returns:
            number of not `SELECT` statement ( `INSERT`, `UPDATE`, `DELETE` )
        """
        return sum(
            1
            for capture_query in self.filtered_captured_queries
            if not capture_query["raw_sql"].startswith("SELECT")
        )

    @property
    def total_count(self) -> int:
        """
        Returns:
            The number of all queries.
        """
        return len(self.filtered_captured_queries)

    @property
    def total_duration(self) -> float:
        """
        Returns:
           The total time the query was executed.
        """
        return sum(
            capture_query["duration"]
            for capture_query in self.filtered_captured_queries
        )

    @cached_property
    def slow_captured_queries(self) -> typing.List[CapturedQuery]:
        """
        Returns:
            [CapturedQuery][capture.CapturedQuery] list with time exceeding [SLOW_MIN_SECOND](home/settings)
        """
        results = []
        slow_min_second = get_config()["PRINT_THRESHOLDS"]["SLOW_MIN_SECOND"]
        if slow_min_second is not None:
            for captured_query in self.filtered_captured_queries:
                if captured_query["duration"] > slow_min_second:
                    results.append(captured_query)

        return results

    @cached_property
    def duplicates_counter(self) -> typing.Counter[CapturedQuery]:
        """
        Returns:
            `Counter` that counts the number of `Duplicate` in all queries except ignore_patterns.
        """
        counter: typing.Counter[CapturedQuery] = Counter()
        for captured_query in self.filtered_captured_queries:
            counter[DuplicateHashableCapturedQuery(captured_query)] += 1  # type: ignore

        return counter

    @cached_property
    def duplicates_counter_over_threshold(self) -> typing.Counter[CapturedQuery]:
        """
        Returns:
            CaptureQuery Counter that exceeds [DUPLICATE_MIN_COUNT](../home/settings.md) among [duplicates_counter][classify.CapturedQueryClassifier.duplicates_counter].
        """
        counter: typing.Counter[CapturedQuery] = Counter()
        duplicate_min_count: typing.Optional[int] = get_config()["PRINT_THRESHOLDS"][
            "DUPLICATE_MIN_COUNT"
        ]
        if duplicate_min_count is not None:
            for captured_query, count in self.duplicates_counter.items():
                if count > duplicate_min_count:
                    counter[captured_query] = count

        return counter

    @cached_property
    def similar_counter(self) -> typing.Counter[CapturedQuery]:
        """
        Returns:
            `Counter` that counts the number of `Similar` in all queries except ignore_patterns.
        """
        counter: typing.Counter[CapturedQuery] = Counter()
        for captured_query in self.filtered_captured_queries:

            counter[SimilarHashableCapturedQuery(captured_query)] += 1  # type: ignore

        return counter

    @cached_property
    def similar_counter_over_threshold(self) -> typing.Counter[CapturedQuery]:
        """
        Returns:
            [CaptureQuery][capture.CapturedQuery] `Counter` that exceeds [SIMILAR_MIN_COUNT](../home/settings.md) among [duplicates_counter][classify.CapturedQueryClassifier.duplicates_counter], it doesn't overlap with Duplicates.
        """
        counter: typing.Counter[CapturedQuery] = Counter()
        similar_min_count: typing.Optional[int] = get_config()["PRINT_THRESHOLDS"][
            "SIMILAR_MIN_COUNT"
        ]
        duplicate_min_count: typing.Optional[int] = get_config()["PRINT_THRESHOLDS"][
            "DUPLICATE_MIN_COUNT"
        ]
        if similar_min_count is not None:
            for captured_query, count in self.similar_counter.items():
                if duplicate_min_count is not None:
                    if (
                        self.duplicates_counter[
                            DuplicateHashableCapturedQuery(captured_query)  # type: ignore
                        ]
                        > duplicate_min_count
                    ):
                        continue
                if count > similar_min_count:
                    counter[captured_query] = count

        return counter

    @property
    def most_common_duplicate(
        self,
    ) -> typing.Union[typing.Tuple[CapturedQuery, int], typing.Tuple[None, None]]:
        """
        Returns:
            most frequent `Counter` among [duplicates_counter][classify.CapturedQueryClassifier.duplicates_counter].
        """
        try:
            return self.duplicates_counter.most_common(1)[0]
        except IndexError:
            return None, None

    @property
    def most_common_similar(
        self,
    ) -> typing.Union[typing.Tuple[CapturedQuery, int], typing.Tuple[None, None]]:
        """
        Returns:
            most frequent `Counter` among [duplicates_counter][classify.CapturedQueryClassifier.similar_counter].
        """
        try:
            return self.similar_counter.most_common(1)[0]
        except IndexError:
            return None, None

    @property
    def has_over_threshold(self) -> bool:
        """
        Returns:
            [SLOW_MIN_SECOND, DUPLICATE_MIN_COUNT, SIMILAR_MIN_COUNT](../home/settings.md)<br>
            If any of the three has exceeded the threshold, return `True`.
        """
        if (
            self.similar_counter_over_threshold
            or self.duplicates_counter_over_threshold
            or self.slow_captured_queries
        ):
            return True
        return False
