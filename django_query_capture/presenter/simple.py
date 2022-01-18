from .base import BasePresenter


class SimplePresenter(BasePresenter):
    """
    only print total queries, duration.
    """

    def print(self) -> None:
        print(
            f'total: {self.classified_query["total"]} queries in {self.classified_query["total_duration"]:.2f} seconds'
        )
