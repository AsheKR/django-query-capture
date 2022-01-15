import re

import sqlparse

from django_query_capture.capture import CapturedQuery
from django_query_capture.utils import get_value_from_django_settings


class BaseLinePrinter:
    @staticmethod
    def get_formatted_sql(captured_query: CapturedQuery) -> str:
        raise NotImplementedError

    @staticmethod
    def is_allow_print(captured_query: CapturedQuery, count: int = 0) -> bool:
        raise NotImplementedError

    @staticmethod
    def is_allow_pattern(query: str) -> bool:
        return not list(
            filter(
                lambda pattern: re.compile(pattern).search(query),
                get_value_from_django_settings("IGNORE_SQL_PATTERNS"),
            )
        )

    @classmethod
    def print(cls, captured_query: CapturedQuery, prefix="", count: int = 0) -> None:
        if cls.is_allow_pattern(captured_query["sql"]) and cls.is_allow_print(
            captured_query, count
        ):
            print(prefix)
            print(cls.get_formatted_sql(captured_query))


class SlowMinTimePrinter(BaseLinePrinter):
    @staticmethod
    def get_formatted_sql(captured_query: CapturedQuery) -> str:
        return f'{sqlparse.format(captured_query["sql"], reindent=True, keyword_case="upper")}'

    @staticmethod
    def is_allow_print(captured_query: CapturedQuery, count: int = 0) -> bool:
        return (
            captured_query["duration"]
            > get_value_from_django_settings("PRINT_THRESHOLDS")["SLOW_MIN_TIME"]
        )

    @classmethod
    def print(
        cls, captured_query: CapturedQuery, prefix: str = "", count: int = 0
    ) -> None:
        super().print(
            captured_query,
            prefix=prefix or f'Slow {captured_query["duration"]:.2f} seconds.',
            count=count,
        )


class DuplicateMinCountPrinter(BaseLinePrinter):
    @staticmethod
    def get_formatted_sql(captured_query: CapturedQuery) -> str:
        return f'{sqlparse.format(captured_query["sql"], reindent=True, keyword_case="upper")}'

    @staticmethod
    def is_allow_print(captured_query: CapturedQuery, count: int = 0) -> bool:
        return (
            count
            > get_value_from_django_settings("PRINT_THRESHOLDS")["DUPLICATE_MIN_COUNT"]
        )

    @classmethod
    def print(
        cls, captured_query: CapturedQuery, prefix: str = "", count: int = 0
    ) -> None:
        super().print(
            captured_query, prefix=prefix or f"Repeated {count} times", count=count
        )


class SimilarMinCountPrinter(BaseLinePrinter):
    @staticmethod
    def get_formatted_sql(captured_query: CapturedQuery) -> str:
        return f'{sqlparse.format(captured_query["raw_sql"], reindent=True, keyword_case="upper")}'

    @staticmethod
    def is_allow_print(captured_query: CapturedQuery, count: int = 0) -> bool:
        return (
            count
            > get_value_from_django_settings("PRINT_THRESHOLDS")["SIMILAR_MIN_COUNT"]
        )

    @classmethod
    def print(
        cls, captured_query: CapturedQuery, prefix: str = "", count: int = 0
    ) -> None:
        super().print(
            captured_query, prefix=prefix or f"Similar {count} times", count=count
        )
