from django_query_capture.presenter.base import BasePresenter
from django_query_capture.utils import colorize, get_stack_prefix


class OnlySlowQueryPresenter(BasePresenter):
    """
    Only queries exceeding the [SLOW_MIN_SECOND](../../home/settings.md) threshold are output.
    """

    def print(self) -> None:
        for captured_query in self.classified_query["slow_captured_queries"]:
            print(
                colorize(
                    f'{get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds',
                    is_warning=True,
                )
            )
