"""
The highest level of module.<br>
It is a module responsible for both query capture, classification, and output.
"""
import typing

from contextlib import ContextDecorator, ExitStack

from django.utils.module_loading import import_string

from django_query_capture.capture import native_query_capture
from django_query_capture.classify import CapturedQueryClassifier
from django_query_capture.presenter import BasePresenter
from django_query_capture.settings import get_config


class query_capture(ContextDecorator):
    def __init__(
        self,
        ignore_output: bool = False,
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        """
        Args:
            ignore_output: Flag to prevent output.
            ignore_patterns: A list of patterns to ignore IGNORE_SQL_PATTERNS of settings.
        """
        self.ignore_output = ignore_output
        self.ignore_patterns = ignore_patterns or get_config()["IGNORE_SQL_PATTERNS"]
        self.presenter_cls: typing.Type[BasePresenter] = import_string(
            get_config()["PRESENTER"]
        )

    def __enter__(self) -> native_query_capture:
        r"""
        Call [native_query_capture.\_\_enter\_\_][capture.native_query_capture.__enter__]

        Returns:
            [native_query_capture][capture.native_query_capture]
        """
        self._exit_stack = ExitStack().__enter__()
        self.native_query_capture = native_query_capture()
        self._exit_stack.enter_context(self.native_query_capture)
        return self.native_query_capture

    def __exit__(self, exc_type, exc_val, exc_tb):
        r"""
        Call [native_query_capture.\_\_exit\_\_][capture.native_query_capture.__exit__].<br>
        Run the [CapturedQueryClassifier][classify.CapturedQueryClassifier] to extract meaningful data and transfer the data to the Presenter.<br>
        Presenter can be changed in settings, and if [BasePresenter][presenter.base.BasePresenter] is inherited and implemented, the desired output can be generated.
        """
        self.classifier = CapturedQueryClassifier(
            self.native_query_capture.captured_queries,
            ignore_patterns=self.ignore_patterns,
        )()
        if not self.ignore_output:
            self.presenter_cls(self.classifier).print()
        self._exit_stack.close()
