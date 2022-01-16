import sqlparse

from .base import BasePresenter


class RawLinePresenter(BasePresenter):
    def print(self) -> None:
        print(
            f"read: {self.read_count}\n",
            f"writes: {self.write_count}\n",
            f"total: {self.total}\n",
            f"total_duration: {self.total_duration:.2f}\n",
            f"most_common_duplicates: {self.most_common_duplicate[1] if self.most_common_duplicate else 0}\n",
            f"most_common_similar: {self.most_common_similar[1] if self.most_common_similar else 0}\n",
        )

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
