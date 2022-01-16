from ..capture import CapturedQuery
from ..utils import colorize
from .base import BasePresenter


class OnlySlowQueryPresenter(BasePresenter):
    def get_stack_prefix(self, captured_query: CapturedQuery):
        return f'[{captured_query["function_name"]}, {captured_query["file_name"]}:{captured_query["line_no"]}]'

    def print(self) -> None:
        for captured_query in self.classified_query["slow_captured_queries"]:
            print(
                colorize(
                    f'{self.get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds',
                    is_warning=True,
                )
            )
