import typing

from contextlib import ContextDecorator, ExitStack

from django.utils.module_loading import import_string

from .capture import native_query_capture
from .classify import CapturedQueryClassifier
from .presenter import BasePresenter
from .utils import get_value_from_django_settings

__all__ = [
    "BasePresenter",
    "query_capture",
    "native_query_capture",
]


class query_capture(ContextDecorator):
    def __init__(self):
        self._exit_stack = ExitStack().__enter__()
        self.native_query_capture = native_query_capture()
        self.presenter_cls: typing.Type[BasePresenter] = import_string(
            get_value_from_django_settings("PRESENTER")
        )

    def __enter__(self):
        self._exit_stack.enter_context(self.native_query_capture)
        return self.native_query_capture

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.presenter_cls.print(
            CapturedQueryClassifier(self.native_query_capture.captured_queries)()
        )
        self._exit_stack.close()
