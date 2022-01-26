"""
Test utility to help you check Duplicate, Similar, and Slow queries in the test
"""
import typing

from contextlib import ContextDecorator, ExitStack

from django.test import override_settings
from django.utils.module_loading import import_string

from django_query_capture import BasePresenter, query_capture
from django_query_capture.settings import get_config
from django_query_capture.utils import CaptureStdOutToString


class AssertInefficientQuery(ContextDecorator):
    def __init__(
        self,
        num: typing.Optional[int] = None,
        seconds: typing.Optional[int] = None,
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        """
        Args:
            num: `Duplicate`, `Similar` Threshold, The value of the setting is ignored.
            seconds: `Slow` Threshold, The value of the setting is ignored.
            ignore_patterns: A list of patterns to ignore IGNORE_SQL_PATTERNS of settings.
        """
        self.ignore_patterns = ignore_patterns or get_config()["IGNORE_SQL_PATTERNS"]
        self.num = num
        self.seconds = seconds
        self.presenter_cls: typing.Type[BasePresenter] = import_string(
            get_config()["PRESENTER"]
        )

    def __enter__(self):
        """
        Run [query_capture.__enter__][decorators.query_capture] and `override_settings.__enter__`
        At this time, the `ignore_output=True` is set so that the output of [query_capture][decorators.query_capture] can be ignored.
        override_settings are used to ignore existing set values within the current context.
        """
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
        """
        End the context of [query_capture][decorators.query_capture] and override_settings.
        And if there is an item above the threshold, the test fails and the failed content is printed.
        """
        self._exit_stack.close()

        with CaptureStdOutToString() as stdout:
            self.presenter_cls(self.query_capture.classifier).print()
            result = stdout.getvalue()
        if self.query_capture.classifier["has_over_threshold"]:
            raise AssertionError(result)
