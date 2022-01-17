import typing

from contextlib import ContextDecorator, ExitStack

from django.test import override_settings

from django_query_capture import query_capture
from django_query_capture.settings import get_config
from django_query_capture.utils import get_stack_prefix, truncate_string


class AssertInefficientQuery(ContextDecorator):
    def __init__(
        self,
        test_case,
        num: int = 0,
        seconds: int = 0,
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        self.test_case = test_case
        self.ignore_patterns = ignore_patterns or get_config()["IGNORE_SQL_PATTERNS"]
        self.num = num
        self.seconds = seconds

    def __enter__(self):
        self._exit_stack = ExitStack().__enter__()
        self.query_capture = query_capture(ignore_output=True)
        config = get_config().copy()
        config.update(
            {
                "PRINT_THRESHOLDS": {
                    **config["PRINT_THRESHOLDS"],
                    "SLOW_MIN_SECOND": self.seconds,
                    "DUPLICATE_MIN_COUNT": self.num,
                    "SIMILAR_MIN_COUNT": self.num,
                }
            }
        )
        self._exit_stack.enter_context(override_settings(QUERY_CAPTURE=config))
        self._exit_stack.enter_context(self.query_capture)
        return self.query_capture

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_stack.close()
        classifier = self.query_capture.classifier
        result = ""
        if classifier["duplicates_counter_over_threshold"]:
            for captured_query, count in classifier[
                "duplicates_counter_over_threshold"
            ].items():
                result += f'\n{get_stack_prefix(captured_query)} Duplicates {count} times: {truncate_string(captured_query["sql"], 25)}'

        if classifier["similar_counter_over_threshold"]:
            for captured_query, count in classifier[
                "similar_counter_over_threshold"
            ].items():
                result += f'\n{get_stack_prefix(captured_query)} Similar {count} times: {truncate_string(captured_query["raw_sql"], 25)}'

        if classifier["slow_captured_queries"]:
            for captured_query in classifier["slow_captured_queries"]:
                result += f'\n{get_stack_prefix(captured_query)} Slow {captured_query["duration"]:.2f} seconds: {truncate_string(captured_query["raw_sql"], 25)}'

        self.test_case.assertFalse(bool(result), result)
