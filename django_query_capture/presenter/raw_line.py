from django_query_capture.classify import ClassifiedQuery

from ..printer import (
    DuplicateMinCountPrinter,
    SimilarMinCountPrinter,
    SlowMinTimePrinter,
)
from .base import BasePresenter


class RawLinePresenter(BasePresenter):
    @staticmethod
    def print(classified_query: ClassifiedQuery) -> None:
        print(
            f'\ntotal: {classified_query["total"]}\n'
            f'read: {classified_query["read"]}\n'
            f'writes: {classified_query["writes"]}\n'
            f'total_duration: {classified_query["total_duration"]:.2f}\n'
            f'most_common_duplicates: {classified_query["most_common_duplicates"]}\n'
            f'most_common_similar: {classified_query["most_common_similar"]}\n'
        )

        for captured_query in classified_query["captured_queries"]:
            SlowMinTimePrinter.print(captured_query)

        for captured_query, count in classified_query["duplicates_counter"].items():
            DuplicateMinCountPrinter.print(captured_query, count=count)

        for captured_query, count in classified_query["similar_counter"].items():
            SimilarMinCountPrinter.print(captured_query, count=count)
