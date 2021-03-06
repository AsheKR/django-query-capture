"""
This module is a code that expands and holds data by hooking whenever a query occurs in django.
"""

import typing

import inspect
import time
from contextlib import ContextDecorator, ExitStack
from distutils.sysconfig import get_python_lib

from django.db import connection
from django.db.backends.dummy.base import DatabaseWrapper
from django.db.backends.utils import CursorWrapper


class CapturedQueryContext(typing.TypedDict):
    """
    It is a `data class` that captures the data that appears as Context when you capture Query in django.
    """

    connection: DatabaseWrapper
    cursor: CursorWrapper


class CapturedQuery(typing.TypedDict):
    """
    A `data class` that adds the time and place of occurrence to the data that comes out when you capture Query in django.
    """

    sql: str
    raw_sql: str
    raw_params: str
    many: bool
    duration: float
    file_name: str
    function_name: str
    line_no: int
    context: CapturedQueryContext


class native_query_capture(ContextDecorator):
    """
    This is the `ContextDecorator` that extends django's `connection.execute_wrapper`.<br>
    measure the time of the query and guess where the query occurred.<br>
    the main attribute is [self.captured_queries][capture.CapturedQuery], [native_query_capture][capture.native_query_capture] returns data from some captured_queries.
    """

    def __init__(self):
        """
        `self._exit_stack`: `ExitStack` was used to wrap `connection.execute_wrapper`.<br>
        `self.captured_queries`: Used to store captured queries and expanded data.
        """
        self._exit_stack = ExitStack().__enter__()
        self.captured_queries: typing.List[CapturedQuery] = []

    def __enter__(self) -> "native_query_capture":
        """
        Use exit_stack to perform `connection.execute_wrapper.__enter__`.

        Returns:
            Returns yourself with the property of [self.captured_queries][capture.CapturedQuery] so that you can check captured queries in real time.
        """
        self._exit_stack.enter_context(connection.execute_wrapper(self._save_queries))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close exit_stack to call `connection.execute_wrapper.__exit___`.
        """
        self._exit_stack.close()

    def __len__(self) -> int:
        """
        Returns:
            Returns the length of [self.captured_queries][capture.CapturedQuery].
        """
        return len(self.captured_queries)

    def _save_queries(self, execute, sql, params, many, context):
        """
        https://docs.djangoproject.com/en/3.2/topics/db/instrumentation/

        It is a function used as a callback for execute_wrapper and receives a factor of `connection.execute_wrapper`.<br>
        measure the time of the query with the data provided by `connection.execute_wrapper`, track and store the query-generated CallStack.

        Args:
            execute: a callable, which should be invoked with the rest of the parameters in order to execute the query.
            sql: a str, the SQL query to be sent to the database.
            params: a list/tuple of parameter values for the SQL command, or a list/tuple of lists/tuples if the wrapped call is executemany().
            many: a bool indicating whether the ultimately invoked call is execute() or executemany() (and whether params is expected to be a sequence of values, or a sequence of sequences of values).
            context: a dictionary with further data about the context of invocation. This includes the connection and cursor.

        Returns:
            Returns the result of the exit for the basic operation of `connection.execute_wrapper`.
        """
        python_library_directory = get_python_lib()
        called_by = [
            stack
            for stack in inspect.stack()
            if not stack.filename.startswith(python_library_directory)
        ][0]
        file_name = called_by.filename
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
