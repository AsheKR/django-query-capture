import re

from django_query_capture.classify import ClassifiedQuery
from django_query_capture.settings import get_config


class BasePresenter:
    @staticmethod
    def print(classified_query: ClassifiedQuery) -> None:
        raise NotImplementedError

    @staticmethod
    def is_allow_pattern(query: str) -> bool:
        return not list(
            filter(
                lambda pattern: re.compile(pattern).search(query),
                get_config()["IGNORE_SQL_PATTERNS"],
            )
        )
