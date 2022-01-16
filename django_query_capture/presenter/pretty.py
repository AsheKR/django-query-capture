import sqlparse
from tabulate import tabulate

from django_query_capture.settings import get_config
from django_query_capture.utils import colorize

from .base import BasePresenter


class PrettyPresenter(BasePresenter):
    @staticmethod
    def is_printable_type(value):
        return isinstance(value, (str, int, float))

    @staticmethod
    def format_print_value(value):
        return f"{value:.2f}" if isinstance(value, float) else value

    def get_stats_table(self, is_warning: bool = False) -> str:
        return colorize(
            tabulate(
                [
                    [
                        self.read_count,
                        self.write_count,
                        self.total,
                        f"{self.total_duration:.2f}",
                        self.most_common_duplicate[1]
                        if self.most_common_duplicate
                        else 0,
                        self.most_common_similar[1] if self.most_common_similar else 0,
                    ]
                ],
                [
                    "read",
                    "writes",
                    "total",
                    "total_duration",
                    "most_common_duplicates",
                    "most_common_similar",
                ],
                tablefmt=get_config()["PRETTY"]["TABLE_FORMAT"],
            ),
            is_warning,
        )

    def print(self) -> None:
        is_warning = self.has_over_threshold
        print("\n" + self.get_stats_table(is_warning))

        for captured_query in self.slow_captured_queries:
            print(f'Slow {captured_query["duration"]:.2f} seconds')
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )

        for captured_query, count in self.duplicates_counter_over_threshold.items():
            print(f"Repeated {count} times")
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )

        for captured_query, count in self.similar_counter_over_threshold.items():
            print(f"Similar {count} times")
            print(
                sqlparse.format(
                    captured_query["sql"], reindent=True, keyword_case="upper"
                )
            )
