import typing

import inspect
import time
from contextlib import ContextDecorator, ExitStack

from django.db import connection
from django.db.backends.dummy.base import DatabaseWrapper
from django.db.backends.utils import CursorWrapper


class CapturedQueryContext(typing.TypedDict):
    connection: DatabaseWrapper
    cursor: CursorWrapper


class CapturedQuery(typing.TypedDict):
    sql: str
    raw_sql: str
    raw_params: str
    many: bool
    duration: float
    file_name: str
    function_name: str
    line_no: str
    context: CapturedQueryContext


class native_query_capture(ContextDecorator):
    def __init__(self):
        self._exit_stack = ExitStack().__enter__()
        self.captured_queries: typing.List[CapturedQuery] = []

    def __enter__(self):
        self._exit_stack.enter_context(connection.execute_wrapper(self._save_queries))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_stack.close()

    def __len__(self):
        return len(self.captured_queries)

    def _save_queries(self, execute, sql, params, many, context):
        call_stack = [
            stack for stack in inspect.stack() if "site-packages" not in stack.filename
        ]
        called_by = call_stack[1]
        file_name = called_by.filename.split("/")[-1]
        function_name = called_by.function
        line_no = called_by.lineno
        start_timestamp = time.monotonic()
        result = execute(sql, params, many, context)
        duration = time.monotonic() - start_timestamp
        self.captured_queries.append(
            {
                "sql": sql % tuple(params) if params else sql,
                "raw_sql": sql,
                "raw_params": params,
                "many": many,
                "duration": duration,
                "file_name": file_name,
                "function_name": function_name,
                "line_no": line_no,
                "context": context,
            }
        )

        return result
