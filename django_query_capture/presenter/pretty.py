import sqlparse
from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.sql import SqlLexer
from tabulate import tabulate

from django_query_capture.presenter.base import BasePresenter
from django_query_capture.settings import get_config
from django_query_capture.utils import colorize, get_stack_prefix


class PrettyPresenter(BasePresenter):
    """
    Outputs all elements of [ClassifiedQuery][classify.ClassifiedQuery] with formatting.<br>
    termscolor: [https://github.com/django/django/blob/main/django/utils/termcolors.py](https://github.com/django/django/blob/main/django/utils/termcolors.py)<br>
    tabulate: [https://github.com/astanin/python-tabulate#table-format](https://github.com/astanin/python-tabulate#table-format) <br>
    pygments: [https://pygments.org/styles/](https://pygments.org/styles/)
    """

    @staticmethod
    def print_sql(sql: str) -> None:
        print(
            highlight(
                sqlparse.format(sql, reindent=True, keyword_case="upper"),
                SqlLexer(),
                TerminalTrueColorFormatter(
                    style=get_config()["PRETTY"]["SQL_COLOR_FORMAT"]
                ),
            )
        )

    def get_stats_table(self, is_warning: bool = False) -> str:
        return colorize(
            tabulate(
                [
                    [
                        self.classified_query["read"],
                        self.classified_query["writes"],
                        self.classified_query["total"],
                        f"{self.classified_query['total_duration']:.2f}",
                        self.classified_query["most_common_duplicate"][1]
                        if self.classified_query["most_common_duplicate"]
                        else 0,
                        self.classified_query["most_common_similar"][1]
                        if self.classified_query["most_common_similar"]
                        else 0,
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
        is_warning = self.classified_query["has_over_threshold"]
        print("\n" + self.get_stats_table(is_warning))

        for captured_query in self.classified_query["slow_captured_queries"]:
            print(
                f'{get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds'
            )
            self.print_sql(captured_query["sql"])

        for captured_query, count in self.classified_query[
            "duplicates_counter_over_threshold"
        ].items():
            print(f"{get_stack_prefix(captured_query)} Repeated {count} times")
            self.print_sql(captured_query["sql"])

        for captured_query, count in self.classified_query[
            "similar_counter_over_threshold"
        ].items():
            print(f"{get_stack_prefix(captured_query)} Similar {count} times")
            self.print_sql(captured_query["raw_sql"])
