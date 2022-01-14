import re

import sqlparse

from django_query_capture.classify import ClassifiedQuery
from django_query_capture.utils import get_value_from_django_settings


class BasePresenter:
    def __init__(self, classified_query: ClassifiedQuery):
        self.classified_query = classified_query

    def print(self):
        raise NotImplementedError


class RawLinePresenter(BasePresenter):
    def print(self):
        print(
            f'\ntotal: {self.classified_query["total"]}\n'
            f'read: {self.classified_query["read"]}\n'
            f'writes: {self.classified_query["writes"]}\n'
            f'total_duration: {self.classified_query["total_duration"]:.2f}\n'
            f'most_common_duplicates: {self.classified_query["most_common_duplicates"]}\n'
            f'most_common_similar: {self.classified_query["most_common_similar"]}\n'
        )

        for captured_query in self.classified_query["captured_queries"]:
            SlowMinTimePrinter.print(
                captured_query["sql"], duration=captured_query["duration"]
            )

        for query, count in self.classified_query["duplicates_counter"].items():
            DuplicateMinCountPrinter.print(query, count=count)

        for query, count in self.classified_query["similar_counter"].items():
            SimilarMinCountPrinter.print(query, count=count)


class BaseLinePrinter:
    @staticmethod
    def is_allow_print(query: str, **kwargs) -> bool:
        raise NotImplementedError

    @staticmethod
    def is_allow_pattern(query: str) -> bool:
        return not filter(
            lambda pattern: re.compile(pattern).search(query),
            get_value_from_django_settings("IGNORE_SQL_PATTERNS"),
        )

    @classmethod
    def print(cls, query: str, prefix: str = "", **kwargs) -> None:
        if cls.is_allow_pattern(query) and cls.is_allow_print(query, **kwargs):
            if prefix and not prefix.endswith("\n"):
                prefix += "\n"
            print(
                prefix, f'{sqlparse.format(query, reindent=True, keyword_case="upper")}'
            )


class SlowMinTimePrinter(BaseLinePrinter):
    @staticmethod
    def is_allow_print(query: str, duration: float = 0) -> bool:
        return (
            duration
            > get_value_from_django_settings("PRINT_THRESHOLDS")["SLOW_MIN_TIME"]
        )

    @classmethod
    def print(cls, query: str, prefix: str = "", duration: float = 0) -> None:
        super().print(query, prefix=f"Slow {duration:.2f} seconds", duration=duration)


class DuplicateMinCountPrinter(BaseLinePrinter):
    @staticmethod
    def is_allow_print(query: str, count: int = 0) -> bool:
        return (
            count
            > get_value_from_django_settings("PRINT_THRESHOLDS")["DUPLICATE_MIN_COUNT"]
        )

    @classmethod
    def print(cls, query: str, prefix: str = "", count: int = 0) -> None:
        super().print(query, prefix=f"Repeated {count} times", count=count)


class SimilarMinCountPrinter(BaseLinePrinter):
    @staticmethod
    def is_allow_print(query: str, count: int = 0) -> bool:
        return (
            count
            > get_value_from_django_settings("PRINT_THRESHOLDS")["SIMILAR_MIN_COUNT"]
        )

    @classmethod
    def print(cls, query: str, prefix: str = "", count: int = 0) -> None:
        super().print(query, prefix=f"Similar {count} times", count=count)
