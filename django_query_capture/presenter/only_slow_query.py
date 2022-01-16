from ..capture import CapturedQuery
from ..utils import colorize, get_stack_prefix
from .base import BasePresenter


class OnlySlowQueryPresenter(BasePresenter):
    def print(self) -> None:
        for captured_query in self.classified_query["slow_captured_queries"]:
            print(
                colorize(
                    f'{get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds',
                    is_warning=True,
                )
            )
