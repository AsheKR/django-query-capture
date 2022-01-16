import typing

from contextlib import ContextDecorator, ExitStack

from django.utils.module_loading import import_string

from . import native_query_capture
from .classify import CapturedQueryClassifier
from .presenter import BasePresenter
from .settings import get_config


class query_capture(ContextDecorator):
    def __init__(
        self,
        ignore_output: bool = False,
        ignore_patterns: typing.Optional[typing.List[str]] = None,
    ):
        self.ignore_output = ignore_output
        self.ignore_patterns = ignore_patterns or get_config()["IGNORE_SQL_PATTERNS"]
        self.presenter_cls: typing.Type[BasePresenter] = import_string(
            get_config()["PRESENTER"]
        )

    def __enter__(self):
        self._exit_stack = ExitStack().__enter__()
        self.native_query_capture = native_query_capture()
        self._exit_stack.enter_context(self.native_query_capture)
        return self.native_query_capture

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.classifier = CapturedQueryClassifier(
            self.native_query_capture.captured_queries,
            ignore_patterns=self.ignore_patterns,
        )()
        if not self.ignore_output:
            self.presenter_cls(self.classifier).print()
        self._exit_stack.close()
