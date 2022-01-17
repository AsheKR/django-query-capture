import sqlparse

from django_query_capture.presenter.base import BasePresenter
from django_query_capture.utils import get_stack_prefix


class RawLinePresenter(BasePresenter):
    """
    Outputs all elements of [ClassifiedQuery][classify.ClassifiedQuery] without formatting.
    """

    def print(self) -> None:
        print(
            f"read: {self.classified_query['read']}\n",
            f"writes: {self.classified_query['writes']}\n",
            f"total: {self.classified_query['total']}\n",
            f"total_duration: {self.classified_query['total_duration']:.2f}\n",
            f"most_common_duplicates: {self.classified_query['most_common_duplicate'][1] if self.classified_query['most_common_duplicate'] else 0}\n",
            f"most_common_similar: {self.classified_query['most_common_similar'][1] if self.classified_query['most_common_similar'] else 0}\n",
        )

        for captured_query in self.classified_query["slow_captured_queries"]:
            print(
                f'{get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds'
            )
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )

        for captured_query, count in self.classified_query[
            "duplicates_counter_over_threshold"
        ].items():
            print(f"{get_stack_prefix(captured_query)} Repeated {count} times")
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )

        for captured_query, count in self.classified_query[
            "similar_counter_over_threshold"
        ].items():
            print(f"{get_stack_prefix(captured_query)} Similar {count} times")
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )
