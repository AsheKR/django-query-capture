from django_query_capture.classify import DuplicateHashableCapturedQueryDict
from django_query_capture.settings import get_config

from ..printer import (
    DuplicateMinCountPrinter,
    SimilarMinCountPrinter,
    SlowMinTimePrinter,
)
from .base import BasePresenter


class RawLinePresenter(BasePresenter):
    def print(self) -> None:
        print(
            f'\ntotal: {self._classified_query["total"]}\n'
            f'read: {self._classified_query["read"]}\n'
            f'writes: {self._classified_query["writes"]}\n'
            f'total_duration: {self._classified_query["total_duration"]:.2f}\n'
            f'most_common_duplicates: {self._classified_query["most_common_duplicates"]}\n'
            f'most_common_similar: {self._classified_query["most_common_similar"]}\n'
        )

        for captured_query in self._classified_query["captured_queries"]:
            SlowMinTimePrinter.print(captured_query)

        for captured_query, count in self._classified_query[
            "duplicates_counter"
        ].items():
            DuplicateMinCountPrinter.print(captured_query, count=count)

        for captured_query, count in self._classified_query["similar_counter"].items():
            duplicated_hashable_captured_query = DuplicateHashableCapturedQueryDict(
                captured_query
            )
            if (
                duplicated_hashable_captured_query
                in self._classified_query["duplicates_counter"]
                and self._classified_query["duplicates_counter"][
                    duplicated_hashable_captured_query
                ]
                > get_config()["PRINT_THRESHOLDS"]["DUPLICATE_MIN_COUNT"]
            ):
                continue
            SimilarMinCountPrinter.print(captured_query, count=count)
